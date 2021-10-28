import logging


class Request:
    def __init__(self, method, path, headers, isDir):
        self.method = method
        self.path = path
        self.headers = headers
        self.isDir = isDir

        logging.debug('isDir: ' + str(isDir))
        if len(path.split('/')[-1].split('.')) == 1:
            logging.debug('got the directory')
            self.path += '/index.html' if self.path[-1] != '/' else 'index.html'
