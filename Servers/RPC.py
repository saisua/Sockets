import xmlrpc.server
from multithr import Process
from Languages.Server_lang import lang

def main():
    pass

class RPC():
    def __init__(self, identifier:str, ip:str="localhost", port:int=0, server:"Server"=None):
        self.ip = str(ip)
        self.port = int(port)

        self.server = server

        self.identifier = identifier

        self._socket = xmlrpc.server.SimpleXMLRPCServer((self.ip, self.port), encoding="utf-8")

    # Shared functions
   
    def __enter__(self):
        self.open()

    def open(self):
        with SimpleXMLRPCServer(("localhost", 8000)) as server:
            server.register_function(pow)
            server.register_function(lambda x,y: x+y, 'add')
            server.register_instance(ExampleService(), allow_dotted_names=True)
            server.register_multicall_functions()
            print('Serving XML-RPC on localhost port 8000')
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("\nKeyboard interrupt received")

    def __exit__(self):
        pass

if __name__ == "__main__":
    main()
else: print("Imported RPC Server")
