# HTTPServer
HTTPServer de testes escrito em Python 3

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
