import xmlrpc.server

def main():
    pass

class RCP():
    def __init__(self, ip:str="localhost", port:int=12412, locks:tuple["Lock"]=()):
        self.ip = str(ip)
        self.port = int(port)

        self.locks = locks

        self._socket = xmlrpc.server.SimpleXMLRPCServer((self.ip, self.port), encoding="utf-8")

    def __enter__(self):
        pass

    def __close__(self):
        pass

if __name__ == "__main__":
    main()