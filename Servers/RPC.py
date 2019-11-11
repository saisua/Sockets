import xmlrpc.server
from multithr import Process
from Languages.Server_lang import lang

def main():
    pass

class RPC():
    def __init__(self, ip:str="localhost", port:int=0, locks:tuple=()):
        self.ip = str(ip)
        self.port = int(port)

        self.locks = locks

        self._socket = xmlrpc.server.SimpleXMLRPCServer((self.ip, self.port), encoding="utf-8")

    # Shared functions
   
    def __enter__(self):
        pass

    def __exit__(self):
        pass

if __name__ == "__main__":
    main()
else: print("Imported RPC Server")