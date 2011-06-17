#!/usr/bin/env python
import re
import sys
import time

import urlparse
import BaseHTTPServer
import ConfigParser

SERVICE = 'skeleton'

config = ConfigParser.ConfigParser()
configs = [
    '%(service)s.conf',
    '/etc/%(service)s.conf',
    '%(scriptdir)s/%(service)s.conf'
]
if not sys.path[0]:
    sys.path[0] = '.'
config.read(map(lambda x: x % {'scriptdir': sys.path[0], 'service': SERVICE}, configs))

PORT = config.getint(SERVICE, 'tcpport')


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    # Disable logging DNS lookups
    def address_string(self):
        return str(self.client_address[0])

    def do_GET(self):
        start = time.time()

        self.url = urlparse.urlparse(self.path)
        self.params = urlparse.parse_qs(self.url.query)

        def html_ok():
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_index():
            html_ok()

            self.wfile.write('Path: %s\n' % repr(self.path))
            self.wfile.write('Params: %s\n' % repr(self.params))

        dispatches = [
            ('^/.*$', do_index),
        ]
        for pattern, dispatch in dispatches:
            m = re.match(pattern, self.path)
            if m:
                dispatch(*m.groups())
                break

        else:
            self.send_error(500)

        end = time.time()
        print 'Time taken: %0.3f ms' % ((end - start) * 1000)


httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
print 'Started on port %s' % PORT
httpd.serve_forever()

