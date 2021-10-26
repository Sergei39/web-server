import sys
import logging

from internal.server.server import HTTPServer
from internal.utils import read_config

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    serv = HTTPServer(read_config(sys.argv[1]))
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
