from urlparse import urlparse, parse_qs
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class Server(HTTPServer):

    pipe = None

    def __init__(self, *args, **kwargs):
        self.pipe = kwargs.pop('pipe')
        HTTPServer.__init__(self, *args, **kwargs)

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        result = urlparse(self.path)
        qs = parse_qs(result.query)
        try:
            self.server.pipe.send(qs['code'][0])
        except IndexError:
            pass
        self.server.pipe.close()
        self.send_response(200)
