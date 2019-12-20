import rpyc
from rpyc import ThreadedServer
from rpyc.utils.teleportation import export_function,import_function
import sys
import time

sys.path.append(sys.path[0][:-7])

from multiprocessing import Process, Manager
from Languages.Server_lang import lang

def main():
    serv = RPC('1',ip=input("ip > ")or"localhost",port=12412,start_on_connect=False)
    serv.to_run = cpu
    serv.args = [(50000000*i,50000000*(i+1)) for i in range(10)]
    a = Process(target=serv.open,daemon=True)
    a.start()

    input()
    print(serv.result)
    serv.run()
    time.sleep(15)
    print(serv.result)    
    a.join()

    print(sum(serv.result))

def cpu(f,t):
    b = 0
    for a in range(f,t):
        b += a
    return b

class RPC(rpyc.Service):
    def __init__(self, identifier:str, ip:str="localhost", port:int=0, server:"Server"=None,
                *,start_on_connect:bool=True):
        print("RPC.__init__")
        self.ip = str(ip)
        self.port = int(port)

        self.server = server

        if(server is None): self._manager = Manager()
        else: self._manager = server._manager

        self._clients = []
        self.__client_num = None

        self.client_start = []
        self.default_start = start_on_connect

        self.identifier = identifier

        self._socket = None

        self._run = None

        self.__to_run = None
        self.args = [()]

        self.result = self._manager.list()

    # Shared functions
   
    def __enter__(self):
        self.open()

    def __exit__(self):
        pass

    def open(self):
        self._socket = ThreadedServer(self, hostname=self.ip, port=self.port)
        self._socket.start()
        print(f"Open server ({self._socket}) in \n{self.ip}:{self.port}")

    def on_connect(self, conn):
        self.__client_num = len(self._clients)
        self.client_start.append(self.default_start)

        self._clients.append(self)
        print(f"New client (number {self.__client_num})")
        return super().on_connect(conn)

    def exposed_set_run(self, run_funct):
        self._run = run_funct

    def exposed_run_run(self):
        if(self._run is None): return -1
        #print(self._run(self.to_run, *self.args[self.__client_num]))
        self.result.append(self._run(self.to_run, *self.args[self.__client_num]))
        print(self.result)
        #run = rpyc.async_(self._run)

        #self.result.append(run)
        #self._run(self.to_run, *self.args[self.__client_num])

    def run(self):
        for obj in self._clients:
            obj.exposed_run_run()

    def get_to_run(self):
        return self.__to_run
    def set_to_run(self, new_to_run):
        self.__to_run = export_function(new_to_run)

    to_run = property(get_to_run, set_to_run)

if __name__ == "__main__":
    main()
else: print("Imported RPC Server")