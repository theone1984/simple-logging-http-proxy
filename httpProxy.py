from optparse import OptionParser
import SimpleHTTPServer
import SocketServer
import urllib2
import time
import string

parser = OptionParser()
parser.add_option("-o", "--host", dest="hostname", help="The hostname to proxy to", default="http://localhost")
parser.add_option("-p", "--port", dest="port", help="Port number to listen to", default=8051)
(options, args) = parser.parse_args()

CONTENT_LENGTH_HEADER = 'Content-Length'
NOT_ALLOWED_HTTP_HEADERS = ['transfer-encoding', 'date', 'server']


class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self._proxy_request()

    def do_POST(self):
        self._proxy_request()

    def _proxy_request(self):
        data = self._get_data()

        self._log_request(data)

        response = self._get_response_from_proxied_server(data)
        self._send_response(response)

    def _get_data(self):
        if CONTENT_LENGTH_HEADER in self.headers:
            inputLength = int(self.headers[CONTENT_LENGTH_HEADER])
            return self.rfile.read(inputLength)
        else:
            return None

    def _log_request(self, data):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        print "\nGot request for %s at %s" % (self.path, current_time)
        print "----------------------- REQUEST START -----------------------------"
        print "Headers:\n%s" % self._reindent(str(self.headers), 2)
        print "Request:\n%s" % self._reindent(self.raw_requestline, 2)
        print "Payload:\n%s" % self._reindent(str(data), 2)
        print "------------------------ REQUEST END ------------------------------"

    def _reindent(self, text, numSpaces):
        return string.join([(numSpaces * ' ') + string.lstrip(line) for line in text.split('\n')], '\n')

    def _get_response_from_proxied_server(self, data):
        request = urllib2.Request(options.hostname + self.path)
        for key, value in self.headers.items():
            request.add_header(key, value)
        if data is not None:
            request.add_data(data)

        return urllib2.urlopen(request)

    def _send_response(self, response):
        data = response.read()

        self.protocol_version = "HTTP/1.1"
        self.send_response(response.code, response.msg)
        del self.headers['Server']
        for key, value in response.headers.items():
            if key not in NOT_ALLOWED_HTTP_HEADERS:
                self.send_header(key, value)
        self.end_headers()

        self.wfile.write(data)
        self.finish()


httpd = SocketServer.TCPServer(("", int(options.port)), Proxy)

print "Proxy serving at port %d" % int(options.port)
httpd.serve_forever()