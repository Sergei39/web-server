from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


OK = (200, 'OK')
NOT_FOUND = (404, 'Not Found')
SERVER_ERROR = (500, 'Server Error')
NOT_ALLOWED = (405, 'Method Not Allowed')
FORBIDDEN = (403, 'Forbidden')


def init_head_response(status=NOT_ALLOWED, headers=None, body=None):
    resp = Response(status, headers, body)
    resp.body = ''
    return resp


def init_get_response(status=NOT_ALLOWED, headers=None, body=None):
    return Response(status, headers, body)


class Response:
    def __init__(self, status=NOT_ALLOWED, headers=None, body=None):
        self.code_status = status[0]
        self.text_status = status[1]
        self.body = body
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

        if self.code_status == 200:
            self.headers.append(('Content-Length', len(self.body)))
        if self.code_status == 404:
            self.headers.append(('Content-Length', 0))
