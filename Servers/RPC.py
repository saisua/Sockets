import rpyc
from rpyc import ThreadedServer
import sys
import time

sys.path.append(sys.path[0][:-7])

from multiprocessing import Process
from Languages.Server_lang import lang

def main():
    serv = RPC('1',port=12412)
    serv.to_run = cpu
    serv.open()

def cpu():
    b = 0
    for a in range(50000000):
        b += a
    return b

class RPC(rpyc.Service):
    def __init__(self, identifier:str, ip:str="localhost", port:int=0, server:"Server"=None):
        print("RPC.__init__")
        self.ip = str(ip)
        self.port = int(port)

        self.server = server

        self._client_from_addr = {}

        self.identifier = identifier

        self._socket = None

        self._run = None

        self.to_run = None
        self.args = ()

    # Shared functions
   
    def __enter__(self):
        self.open()

    def __exit__(self):
        pass

    def open(self):
        self._socket = ThreadedServer(self, hostname=self.ip, port=self.port)
        self._socket.start()
        print(f"Open server ({self._socket}) in \n{self.ip}:{self.port}")


    def exposed_set_run(self, run_funct):
        self._run = run_funct

    def exposed_run_run(self):
        self._run(self.to_run, *self.args)

if __name__ == "__main__":
    main()
else: print("Imported RPC Server")