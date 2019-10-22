import socket

def main():
    pass

class UDP():
    def __init__(self, ip:str="localhost", port:int=12412, locks:tuple["Lock"]=(), 
                        *,
                        address_family:"socket.AF_*"=socket.AF_INET):
        self.ip = str(ip)
        self.port = int(port)

        self.locks = locks

        self._socket = socket.socket(address_family, socket.SOCK_DGRAM)
        self._socket.bind((self.ip, self.port))

    def __enter__(self):
        pass

    def __close__(self):
        pass

if __name__ == "__main__":
    main()