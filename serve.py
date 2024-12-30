# Tiny Python HTTP server, used to test that curl is able to validate the cert.
from http.server import HTTPServer, SimpleHTTPRequestHandler
from ssl import SSLContext, PROTOCOL_TLS_SERVER
context = SSLContext(PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="chain.pem", keyfile="server-key.pem")
httpd = HTTPServer(('', 8443), SimpleHTTPRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.serve_forever()
