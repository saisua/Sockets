import socket
from multithr import Process
from Languages.Server_lang import lang

def main():
    pass

class UDP():
    def __init__(self, ip:str="localhost", port:int=0, locks:tuple=(), 
                        *,
                        address_family:"socket.AF_*"=socket.AF_INET):
        self.ip = str(ip)
        self.port = int(port)

        self.locks = locks

        self._socket = socket.socket(address_family, socket.SOCK_DGRAM)
        self._socket.bind((self.ip, self.port))

    # Shared functions

    def __enter__(self):
        pass

    def __exit__(self):
        pass

if __name__ == "__main__":
    main()
