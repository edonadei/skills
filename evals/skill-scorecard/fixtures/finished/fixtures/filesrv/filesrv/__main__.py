from http.server import BaseHTTPRequestHandler, HTTPServer

from .app import handle


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, headers, body = handle("GET", self.path)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
