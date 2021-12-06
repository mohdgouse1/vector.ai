import json
from json import JSONEncoder

class JSONObject:
    def __init__(self, dx):
        self.__dict__ = dx

def load():
    try:
        with open("config.json") as cfxfile:
            cfx = json.load(cfxfile, object_hook=JSONObject)
            return cfx
    except Exception:
        raise Exception("Unable to load the application registery. EXIT")

cfx = load()