import json


def read_config(filepath: str) -> dict:
    try:
        config = dict()
        file = open(filepath, "r")
        for line in file:
            params = line.rstrip().split(sep=' ')
            key, val = params[0], params[1]
            config[key] = val
        print(config)
        return config
    except:
        print("Can't open and serialize config")
        exit()
