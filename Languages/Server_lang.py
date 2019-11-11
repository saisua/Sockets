import json
import os.path

class Server_lang():
    def __init__(self, symbols_fname="overwritten.json"):
        if(not os.path.exists(symbols_fname)):
            symbols_fname = "default.json"
        
        with open(f"{__file__[:-14]}{symbols_fname}",'r') as symbols_file:
            self.symbols = json.load(symbols_file)

    def __str__(self): return str(self.symbols)

    def __repr__(self): return self.symbols

    def __getattr__(self, attr):
        value = self.symbols.get(attr, None)
        if(value is None): raise AttributeError()
        return value

lang = Server_lang()