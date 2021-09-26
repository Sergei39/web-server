import sys
import logging
from parse_apache_configs import parse_config

from internal.server.server import HTTPServer


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    host = sys.argv[1]
    port = int(sys.argv[2])
    name = 'localhost'

    # apache_parse_obj = parse_config.ParseApacheConfig(apache_config_path="conf/httpd.conf")
    # apache_config = apache_parse_obj.parse_config()
    #
    # print(apache_config)
    document_root = 'data'

    serv = HTTPServer(host, port, name, document_root)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
