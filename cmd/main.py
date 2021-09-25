import sys
import logging

from internal.server.server import HTTPServer

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    host = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]

    serv = HTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
