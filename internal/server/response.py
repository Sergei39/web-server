import logging
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import os
import socket


OK = (200, 'OK')
NOT_FOUND = (404, 'Not Found')
SERVER_ERROR = (500, 'Server Error')
NOT_ALLOWED = (405, 'Method Not Allowed')
FORBIDDEN = (403, 'Forbidden')

EXTRACTION = {'html': 'text/html',
              'txt': 'text/html',
              'css': 'text/css',
              'js': 'text/javascript',
              'jpg': 'image/jpeg',
              'jpeg': 'image/jpeg',
              'png': 'image/png',
              'gif': 'image/gif',
              'swg': 'application/x-shockwave-flash',
              'swf': 'application/x-shockwave-flash'}


class Response:
    def __init__(self, headers=None, path='', status=OK):
        self.status = status
        self.path = path
        self.init_headers(headers)

    def init_headers(self, headers):
        self.headers = headers
        if headers is None:
            self.headers = []
        self.headers.append(('Server', 'web-server'))

        now = datetime.now()
        stamp = mktime(now.timetuple())
        self.headers.append(('Date', format_date_time(stamp)))
        self.headers.append(('Connection', 'close'))

        if self.status != OK:
            return

        if os.path.isfile(self.path):
            self.headers.append(('Content-Length', os.path.getsize(self.path)))
            self.headers.append(('Content-Type', EXTRACTION[self.path.split('.')[-1]]))
            return

        if not os.path.exists(self.path):
            self.status = NOT_FOUND
            self.headers.append(('Content-Length', 0))
            return

        self.path += '/index.html' if self.path[-1] != '/' else 'index.html'
        if not os.path.isfile(self.path):
            self.status = FORBIDDEN
            self.headers.append(('Content-Length', 0))
            return

        self.headers.append(('Content-Length', os.path.getsize(self.path)))
        self.headers.append(('Content-Type', EXTRACTION[self.path.split('.')[-1]]))


    def send(self, conn, method):
        wfile = conn.makefile('wb')
        # conn.send(status_line.encode('utf-8'), flags=socket.MSG_OOB | socket.MSG_DONTROUTE)

        resp = f'HTTP/1.1 {self.status[0]} {self.status[1]}\r\n'

        if self.headers:
            for (key, value) in self.headers:
                header_line = f'{key}: {value}\r\n'
                resp += header_line

        resp = resp.encode('utf-8') + b'\r\n'
        # wfile.write(resp)
        # wfile.flush()
        conn.send(resp)

        if method == 'GET' and self.status == OK:
            logging.debug("start read and write file")
            with open(self.path, 'rb') as file:
                # resp += file.read()
                # soc.sendall(sendfile)
                # print('file sent')
            # file = os.open(self.path, os.O_RDONLY)
                blocksize = os.path.getsize(self.path)
                offset = 0

                while True:
                    logging.debug(f'offset: {offset}')
                    sent = os.sendfile(wfile.fileno(), file.fileno(), offset, blocksize)
                    wfile.flush()
                    if sent == 0:
                        break  # EOF
                    offset += sent

        # conn.sendall(resp)
        # logging.debug("before flush")
        # wfile.flush()
        # logging.debug("after flush")
        wfile.close()
        logging.debug("send response success")
