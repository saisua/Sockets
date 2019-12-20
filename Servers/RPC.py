import rpyc
from rpyc import ThreadedServer
from rpyc.utils.teleportation import export_function,import_function
import sys
import time

sys.path.append(sys.path[0][:-7])

from multiprocessing import Manager, cpu_count
from multithr import Process
from Languages.Server_lang import lang
from collections.abc import Iterable
from itertools import zip_longest
from math import ceil

def main():
    serv = RPC('1',ip=input("ip > ")or"localhost",port=12412,start_on_connect=False)
    serv.to_run = cpu
    a = Process(target=serv.open)
    a.start()

    input("Press enter to run all clients\n")
    serv.args_parall = serv.divide_threads([(50000000*i,50000000*(i+1)) for i in range(10)])
    serv.run_parall()
    
    input("Press enter to finish\n")
    serv.result_async_values()

    print(sum(serv.result))

def cpu(f,t):
    b = 0
    for a in range(f,t):
        b += a
    return b

### This class is a proof of concept
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

        self.client_threads = self._manager.list()
        self.__threads = cpu_count()

        self.identifier = identifier

        self._socket = None

        self._run = None
        self._run_parall = None

        self.__to_run = None

        self.__args = []
        self.__args_per_client = None
        self.__args_parall = []

        self.result = self._manager.list()

    # Shared functions
   
    def __enter__(self):
        self.open()

    def __exit__(self,_,__,___):
        pass

    def open(self):
        self._socket = ThreadedServer(self, hostname=self.ip, port=self.port)
        self._socket.start()
        print(f"Open server ({self._socket}) in \n{self.ip}:{self.port}")

    def on_connect(self, conn):
        self.__client_num = len(self._clients)
        self.client_start.append(self.default_start)
        self.client_threads.append(0)

        self._clients.append(self)
        print(f"New client (number {self.__client_num})")
        return super().on_connect(conn)

    def exposed_set_threads(self, threads:int):
        self.client_threads[self.__client_num] = threads
        print(f"Client {self.__client_num} has {threads} threads")

    def exposed_set_run(self, run_funct, run_parall=None):
        self._run = run_funct
        self._run_parall = run_parall

    def exposed_run_run(self):
        if(self._run is None): return -1
        
        run = rpyc.async_(self._run)
        self.result.append(run)

        if(not self.__args_per_client is None): 
            run(self.to_run, *self.__args[self.__client_num])
        else: 
            run(self.to_run, *self.__args)

        return run

    def exposed_run_parall(self):
        if(self._run is None): return -1

        run = rpyc.async_(self._run_parall)
        self.result.append(run)

        for args in self.__args_parall:
            run(self.to_run, args)

        return run


    def run(self):
        for obj in self._clients:
            obj.exposed_run_run()

    def run_parall(self):
        for obj in self._clients:
            obj.exposed_run_parall()


    def result_async_values(self):
        # Race condition :(
        for num,r in enumerate(self.result):
            if(hasattr(r,"value") and r.ready):
                self.result[num] = r.value

    def exposed_result_async(self):
        self.result_async_values()

    def divide_eq(self, iterable, n=None, fill=None):
        if(n is None): n = ceil(len(iterable) / (self.__threads + sum(self.client_threads)))
        return zip_longest(*[iter(iterable)]*n, fillvalue=fill)

    def divide_threads(self, iterable):
        prev = self.__threads
        result = [iterable[:prev]]
        for thread in self.client_threads:
            if(prev >= len(iterable)): break

            result.append(iterable[prev:prev+thread])

        return result


    def get_to_run(self):
        return self.__to_run
    def set_to_run(self, new_to_run):
        self.__to_run = export_function(new_to_run)

    def get_args(self):
        return self.__args
    def set_args(self, new_args):
        self.__args = new_args
                
    def get_args_per_client(self):
        return self.__args_per_client
    def set_args_per_client(self, new_args_pc):
        self.__args_per_client = new_args_pc

    def get_args_parall(self):
        return self.__args_parall
    def set_args_parall(self, new_args_parall):
        self.__args_parall = new_args_parall

    to_run = property(get_to_run, set_to_run)
    args = property(get_args,set_args)
    args_per_client = property(get_args_per_client,set_args)
    args_parall = property(get_args_parall,set_args_parall)

if __name__ == "__main__":
    main()
else: print("Imported RPC Server")