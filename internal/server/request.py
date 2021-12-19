import logging


# todo попробовать убрать класс
class Request:
    def __init__(self, method, path, headers, isDir):
        self.method = method
        self.path = path
        self.headers = headers
        self.isDir = isDir
