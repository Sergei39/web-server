import socket
import logging
from copy import copy
import os

from internal.server.request import Request
from internal.server.response import Response
import internal.server.response as st
from internal.parser import HttpParser

RECV_TIMEOUT = 20
BUF_SIZE = 4096

DEFAULT_PORT = 80
DEFAULT_SERVER_NAME = 'localhost'
DEFAULT_DOCUMENT_ROOT = '/var/www/html'
DEFAULT_THREAD_LIMIT = 16


class HTTPServer:
    def __init__(self, config):
        self._port = int(config['port']) if 'port' in config else DEFAULT_PORT
        self._server_name = config['server_name'] if 'server_name' in config else DEFAULT_SERVER_NAME
        self._document_root = config['document_root'] if 'document_root' in config else DEFAULT_DOCUMENT_ROOT
        self._thread_limit = int(config['thread_limit']) if 'thread_limit' in config else DEFAULT_THREAD_LIMIT
        self._fork_pool = []

    def serve_forever(self):
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind(('', self._port))
            serv_sock.listen()
            logging.info('Server start on port: ' + str(self._port))
            self.run_fork_pool(serv_sock)

        finally:
            serv_sock.close()

    def run_fork_pool(self, serv_sock):
        for i in range(self._thread_limit):
            pid = os.fork()
            if pid != 0:
                logging.info("start pid: " + str(pid))
                self._fork_pool.append(pid)

            else:
                while True:
                    conn, _ = serv_sock.accept()
                    # conn.setblocking(True)
                    try:
                        self.serve_client(conn)
                    except Exception as e:
                        print(('Client serving failed', e))
                    finally:
                        logging.info("close connection")
                        # conn.shutdown(1)
                        conn.close()

        logging.info("Wait fork")
        for fork in self._fork_pool:
            os.waitpid(fork, 0)
        logging.info("Server stop")

    def serve_client(self, conn):
        # todo убрать try
        try:
            logging.debug('New connect on pid: ' + str(os.getpid()))
            req = self.parse_request(conn)
            self.handle_request(conn, req)
        except ConnectionResetError:
            conn = None
        except Exception as e:
            logging.error(e)
            self.send_error(conn, e)

        if conn:
            conn.close()

    def parse_request(self, conn):
        logging.debug('Parse request')
        parser = HttpParser()
        conn.settimeout(RECV_TIMEOUT)
        parser.parse_request(conn)

        method = parser.get_method()
        path = parser.get_path()
        headers = parser.get_headers()

        return Request(method, path, headers, os.path.isdir(self._document_root + path))

    def handle_request(self, conn, req):
        logging.debug('Handle request')
        if req.method != 'GET' and req.method != 'HEAD':
            logging.info('Incorrect method: ' + req.method)
            Response(status=st.NOT_ALLOWED).send(conn, req.method)

        self.routing(conn, req)

    def routing(self, conn, req):
        path = copy(req.path)
        logging.debug('method: ' + req.method + ', path: ' + path)

        # with open(self._document_root + path, 'rb') as file:

        Response(path=self._document_root + path).send(conn, req.method)

    def send_error(self, conn, err):
        logging.debug('Send error')
        try:
            status = err.status
            body = (err.body or err.reason).encode('utf-8')
        except:
            status = st.SERVER_ERROR
            body = b'Internal Server Error'
        Response(headers=[('Content-Length', len(body))], status=status).send(conn, '')
