import socket
import logging
from copy import copy
from urllib.parse import unquote
import os

from internal.server.request import Request
from internal.server.response import Response, init_get_response, init_head_response
import internal.server.response as st

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

RECV_TIMEOUT = 20
BUF_SIZE = 4096
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
        data = b""
        parser = HttpParser()
        conn.settimeout(RECV_TIMEOUT)
        while not parser.is_headers_complete():
            try:
                chunk = conn.recv(BUF_SIZE)
            except:
                break
            if not chunk:
                break

            parser.execute(chunk, len(chunk))
            data += chunk
            if data.decode().endswith('\n'):
                break

        method = parser.get_method()
        path = parser.get_path()
        path = unquote(path)
        parser_headers = parser.get_headers()

        return Request(method, path, parser_headers, os.path.isdir(self._document_root + path))

    def handle_request(self, req):
        logging.debug('Handle request')
        # logging.debug('Start sleep')
        # time.sleep(15)
        # logging.debug('Stop sleep')
        if req.method != 'GET' and req.method != 'HEAD':
            logging.info('Incorrect method: ' + req.method)
            return Response(status=st.NOT_ALLOWED, body='')

        return self.routing(req)

    def routing(self, req):
        path = copy(req.path)
        logging.debug('method: ' + req.method + ', path: ' + path)

        try:
            headers = [('Content-Type', EXTRACTION[path.split('.')[-1]])]
            with open(self._document_root + path, 'rb') as file:
                info = file.read()
                return init_get_response(status=st.OK, body=info, headers=headers) \
                    if req.method == 'GET' \
                    else init_head_response(status=st.OK, body=info, headers=headers)
        except (FileNotFoundError, NotADirectoryError):
            status = st.FORBIDDEN if req.isDir else st.NOT_FOUND
            return Response(status=status, body='')

    def send_response(self, conn, resp):
        logging.debug('Send response')
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.code_status} {resp.text_status}\r\n'
        wfile.write(status_line.encode('utf-8'))

        if resp.headers:
            for (key, value) in resp.headers:
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('utf-8'))

        wfile.write(b'\r\n')

        if resp.body:
            wfile.write(resp.body)

        wfile.flush()
        wfile.close()

    def send_error(self, conn, err):
        logging.debug('Send error')
        try:
            status = err.status
            body = (err.body or err.reason).encode('utf-8')
        except:
            status = st.SERVER_ERROR
            body = b'Internal Server Error'
        resp = Response(status,
                        [('Content-Length', len(body))],
                        body)
        self.send_response(conn, resp)
