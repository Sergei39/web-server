import sys
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


class Response:
  def __init__(self, status, headers=None, body=None):
    self.status = status
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

    if self.status == 200:
      self.headers.append(('Content-Length', len(self.body)))
    if self.status == 404:
      self.headers.append(('Content-Length', 0))
