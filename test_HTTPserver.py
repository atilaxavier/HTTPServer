#!/usr/bin/python
"""
Servidor HTTP(S) para testes.
USO: python test_HTTPserver.py
Parametros:
-s - funciona como HTTPS. Usa server_cert.pem e key_cert.pem por default. Se não for usado esse flag, funciona como HTTP.
-i - mostra arquivo /index_example3.html por default. Se não for usado esse flag, mostra arquivos na pasta do servidor.
-p - porta na qual o servidor vai atender requests. Default é 8000
-idxp <nome_arquivo> - indica nome de arquivo .html a ser mostrado.
-cert <arquivo_certificado> - indica nome do arquivo com certificado digital para servidor seguro
-key <arquivo_chave> - indica nome do arquivo com chave do certificado digital para servidor seguro


Para gerar certificado digital do servidor é preciso ter o openssl instalado:
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
OU
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -node
"""
import socket, os
from socketserver import BaseServer
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from io import BytesIO
from os import curdir, sep
import cgi
import ssl
import argparse

#CERT = 'server_cert.pem'
#KEY = 'server_key.pem'
#PORT = 8000
#IDX_PATH = "/index_example3.html"

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		print("\nComando: %s"%self.command)
		print("Linha do request: %s"%self.requestline)
		print("Endereco do cliente: %s"%self.address_string())
		if self.path=="/":
			self.path=IDX_PATH

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				print(self.headers)
				hdrs = ("HEADERS:\n%s"%self.headers).encode()
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				data = ("%s"%f.read()).encode()
				f.close()
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(hdrs)
				self.wfile.write(data)
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
		print("\nComando: %s"%self.command)
		print("Linha do request: %s"%self.requestline)
		print("Endereco do cliente: %s"%self.address_string())
		print(self.headers)	
		if self.path=="/send":
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
						 'CONTENT_TYPE':self.headers['Content-Type'],
			})

			print("Seu nome e: %s\n" % form["your_name"].value)
			self.send_response(200)
			self.end_headers()
			self.wfile.write(("Ok %s , obrigado por usar o meu servidor do teste." % form["your_name"].value).encode())
			return			

class MySimpleHTTPRequestHandler(SimpleHTTPRequestHandler):#BaseHTTPRequestHandler):
	def do_GET(self):
		print("\nComando: %s"%self.command)
		print("Linha do request: %s"%self.requestline)
		print("Endereco do cliente: %s"%self.address_string())
		print(self.headers)
		try:
			if self.path=="/":
				hdrs = ("<p>HEADERS:</p><p>%s</o>"%self.headers).encode()
				mimetype='text/html'
				#lista conteudo do diretorio corrente
				data = ("<p>Lista de arquivos:</p> <p>%s</p>"%"".join(os.listdir())).encode()
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(hdrs)
				self.wfile.write(data)
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
		return super().do_GET()

	def do_POST(self):
		print("\nComando: %s"%self.command)
		print("Linha do request: %s"%self.requestline)
		print("Endereco do cliente: %s"%self.address_string())
		print(self.headers)
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
					 'CONTENT_TYPE':self.headers['Content-Type'],
					})
		print("Recebeu %d valor(es) no post\n" % len(form))
		print("Chaves:")
		print(form.keys())
		for k in form.keys():
			print("Key: %s, value: %s"%(k, form[k].value))
		self.send_response(200)
		mimetype='text/html'
		self.send_header('Content-type',mimetype)
		self.end_headers()
		#self.wfile.write(("Obrigado por usar o meu servidor de teste").encode())	
		data = ("<html><body><h1>Obrigado por usar o meu servidor de teste</h1>")
		data += ("<body><h2>Pares Key : Value recebidos no POST</h2>")
		for k in form.keys():
			data += ("<p>%s : %s</p>"%(k, form[k].value))
		data += ("</body></html>")
		self.wfile.write(data.encode())
		return #super().do_POST()

		
class SecureHTTPServer(HTTPServer):
	def __init__(self, server_address, HandlerClass):
		BaseServer.__init__(self, server_address, HandlerClass)
		ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
		ctx.load_cert_chain(certfile=CERT, keyfile=KEY)
		self.socket = ctx.wrap_socket(socket.socket(self.address_family, self.socket_type), server_side=True)
		self.server_bind()
		self.server_activate()
	
def test(HandlerClass = SimpleHTTPRequestHandler,
		 ServerClass = SecureHTTPServer):
	server_address = ('localhost', PORT) # (address, port)
	try:
		httpd = ServerClass(server_address, HandlerClass)
		sk = httpd.socket
		sa, sp = sk.getsockname()
		print("Servindo em", sa, "port", sp, "...\n")
		httpd.serve_forever()
	except KeyboardInterrupt:
		print ('^C recebido, derrubando servidor web')
		sk.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='test_HTTPserver.py. HTTP Server de teste.')
	parser.add_argument('-s', '--seguro', dest='seguro', default=False, action="store_true",
					help='Define funcionamento como servidor seguro (HTTPS). Se não for configurado funciona como HTTP.')
	parser.add_argument('-i', '--idx_show', dest='idx_show', default=False, action="store_true", 
					help='Define se quer mostrar arquivo html. Se não for configurada, mostra apenas arquivos na pasta do servidor.')										
	parser.add_argument('-idxp', '--idx_path', dest='IDX_PATH', default="/index_example3.html", 
					help='Pasta e nome de arquivo html para mostrar por default.')					
	parser.add_argument('-cert', '--cert_file', dest='CERT', default='server_cert.pem',
						help='Arquivo com certificado para servidor seguro (caso opção -s True seja usada)')
	parser.add_argument('-key', '--key_file', dest='KEY', default='server_key.pem',
					help='Arquivo com chave para servidor seguro (caso opção -s True seja usada)')
	parser.add_argument('-p', '--server_port', dest='PORT', type=int, default=8000,
						help='Porta para o servidor.')
	inarg = parser.parse_args()

	PORT = inarg.PORT
	print("Iniciando servidor HTTP na porta %d."%PORT)
	if inarg.seguro:
		seguro = True
		CERT = inarg.CERT	
		KEY = inarg.KEY
		srv_class = SecureHTTPServer
		print("Servidor HTTPS com arquivo de certficado %s e de chave %s"%(CERT, KEY))
	else:
		seguro = False
		srv_class = HTTPServer
		print("Servidor HTTP sem segurança")

	if inarg.idx_show:	# vamos mostrar arquivo html diferente do padrão
		hdr_class = myHandler
		IDX_PATH = inarg.IDX_PATH
		print("Vai mostrar arquivo %s."%IDX_PATH)
	else:
		hdr_class = MySimpleHTTPRequestHandler
		print("Vai mostrar apenas lista de arquivos do servidor.")
		
	test(HandlerClass = hdr_class, ServerClass = srv_class)
	
	"""
	HandlerClass =
		SimpleHTTPRequestHandler 	# Handler padrão, que mostra arquivos na pasta do servidro
		myHandler					# Handler escrito por mim, que mostra todas as mensagens, e trata arquivo html indicado nos paramtros
	ServerClass = 
		SecureHTTPServer			# Implementa servidro seguro (HTTPS)
		HTTPServer					# Implemetna servidor basico
	"""
	
"""
Para gerar certificado
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
OU
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -node
"""
