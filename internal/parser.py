from urllib.parse import unquote

MAX_LINE = 10 * 64


class HttpParser:

    def __init__(self):
        self.method = None
        self.headers = None
        self.path = None

    def parse_request(self, conn):
        rfile = conn.makefile('rb')
        self.parse_request_line(rfile)
        self.parse_headers(rfile)

    def parse_headers(self, rfile):
        headers = []
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise Exception('Header line is too long')

            if line in (b'\r\n', b'\n', b''):
                # завершаем чтение заголовков
                break

            headers.append(line)

        self.headers = headers

    def parse_request_line(self, rfile):
        raw = rfile.readline(MAX_LINE + 1)
        if len(raw) > MAX_LINE:
            raise Exception('Request line is too long')

        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()

        self.method, path, ver = words
        path = unquote(path)
        self.path = path.split('?')[0]

    def get_method(self):
        return self.method

    def get_path(self):
        return self.path

    def get_headers(self):
        return self.headers
