from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# HTTPRequestHandler class
a_code = ""


class LocalServer(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        global a_code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # print(self.path)
        try:
            qs = parse_qs(urlparse(self.path).query)
            a_code = qs["code"][0]
            # print(a_code[0])
            self.server.stop = True
            message = "Authorization is success, you can close this page now."
        except:
            message = "Hello world!"
        # Send message back to client
        # message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return


class StoppableHTTPServer(HTTPServer):
    """http server that reacts to self.stop flag"""

    def serve_forever(self):
        """Handle one request at a time until stopped."""
        self.stop = False
        while not self.stop:
            self.handle_request()


def run():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', 8080)
    httpd = StoppableHTTPServer(server_address, LocalServer)
    print('running server...')
    httpd.serve_forever()

# run()