import SimpleHTTPServer
import SocketServer
import time
import string

PORT = 8061

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self._pass_request("get")

    def do_POST(self):
        self._pass_request("post")

    def _pass_request(self, method):
        self._log_request()

        self.send_response(200)
        self.send_header('x-test', 'my_header')
        self.send_header('x-method', method)
        self.end_headers()
        self.wfile.write("OK!")

    def _log_request(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        print "\nGot request for %s at %s" % (self.path, current_time)
        print "----------------------- REQUEST START -----------------------------"
        print "Headers:\n%s" % self._reindent(str(self.headers), 2)
        print "Request:\n%s" % self._reindent(self.raw_requestline, 2)
        print "------------------------ REQUEST END ------------------------------"

    def _reindent(self, text, numSpaces):
        return string.join([(numSpaces * ' ') + string.lstrip(line) for line in text.split('\n')], '\n')

httpd = SocketServer.TCPServer(("", PORT), Proxy)

print "Proxy serving at port %d" % PORT
httpd.serve_forever()