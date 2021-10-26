import json
import socket
import logging
import time
from copy import copy
from email.parser import Parser

from internal.server.request import Request
from internal.server.response import Response

MAX_LINE = 64 * 1024
MAX_HEADERS = 100
EXTRACTION = {'html': 'text/html; charset=UTF-8',
              'css': 'text/css',
              'js': 'text/javascript; charset=utf-8',
              'jpg': 'image/jpeg',
              'jpeg': 'image/jpeg',
              'png': 'image/png',
              'gif': 'image/gif',
              'swg': 'application/x-shockwave-flash'}

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 80
DEFAULT_SERVER_NAME = 'localhost'
DEFAULT_DOCUMENT_ROOT = '/var/www/html'


class HTTPServer:
    def __init__(self, config):
        self._port = int(config['port']) if 'port' in config else DEFAULT_PORT
        self._server_name = config['server_name'] if 'server_name' in config else DEFAULT_SERVER_NAME
        self._document_root = config['document_root'] if 'document_root' in config else DEFAULT_DOCUMENT_ROOT

    def serve_forever(self):
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind(('', self._port))
            serv_sock.listen()
            logging.info('Server start on port: ' + str(self._port))

            while True:
                conn, _ = serv_sock.accept()
                try:
                    self.serve_client(conn)
                except Exception as e:
                    print(('Client serving failed', e))
        finally:
            serv_sock.close()

    def serve_client(self, conn):
        try:
            logging.debug('New connect')
            req = self.parse_request(conn)
            resp = self.handle_request(req)
            self.send_response(conn, resp)
        except ConnectionResetError:
            conn = None
        except Exception as e:
            logging.error(e)
            self.send_error(conn, e)

        if conn:
            conn.close()

    def parse_request(self, conn):
        logging.debug('Parse request')
        rfile = conn.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)
        headers = self.parse_headers(rfile)
        host = headers.get('Host')
        if not host:
            raise Exception('Bad request')
        if host not in (self._server_name,
                        f'{self._server_name}:{self._port}'):
            raise Exception('Not found')
        return Request(method, target, ver, headers, rfile)

    def parse_headers(self, rfile):
        logging.debug('Parse headers')
        headers = []
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise Exception('Header line is too long')

            if line in (b'\r\n', b'\n', b''):
                # завершаем чтение заголовков
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS:
                raise Exception('Too many headers')

        sheaders = b''.join(headers).decode('iso-8859-1')
        return Parser().parsestr(sheaders)

    def parse_request_line(self, rfile):
        logging.debug('Parse request line')
        raw = rfile.readline(MAX_LINE + 1)  # эффективно читаем строку целиком
        if len(raw) > MAX_LINE:
            raise Exception('Request line is too long')

        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()  # разделяем по пробелу
        if len(words) != 3:  # и ожидаем ровно 3 части
            raise Exception('Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise Exception('Unexpected HTTP version')

        return method, target, ver

    def handle_request(self, req):
        logging.debug('Handle request')
        # logging.debug('Start sleep')
        # time.sleep(15)
        # logging.debug('Stop sleep')
        if req.method == 'GET':
            return self.routing_get(req)
        elif req.method == 'HEAD':
            return self.routing_head(req)
        else:
            return Response(405, '')

    def routing_get(self, req):
        path = copy(req.path)
        logging.debug('GET ' + path)
        if len(path.split('.')) == 1:
            logging.debug('got the directory')
            path += '/index.html'

        try:
            headers = [('Content-Type', EXTRACTION[path.split('.')[-1]])]
            with open(self._document_root + path, 'rb') as file:
                info = file.read()
                return Response(status=200, body=info, headers=headers)
        except FileNotFoundError:
            return Response(status=404, body='')

    def routing_head(self, req):
        return Response(405, '')

    def send_response(self, conn, resp):
        logging.debug('Send response')
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))

        logging.debug('Send response 1')
        if resp.headers:
            for (key, value) in resp.headers:
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))

        logging.debug('Send response 2')
        wfile.write(b'\r\n')

        logging.debug('Send response 3')
        if resp.body:
            wfile.write(resp.body)

        logging.debug('Send response 4')
        wfile.flush()
        wfile.close()
        logging.debug('Send response 5')

    def send_error(self, conn, err):
        logging.debug('Send error')
        try:
            status = err.status
            body = (err.body or err.reason).encode('utf-8')
        except:
            status = 500
            body = b'Internal Server Error'
        resp = Response(status,
                        [('Content-Length', len(body))],
                        body)
        self.send_response(conn, resp)
