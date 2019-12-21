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
    serv = RPC ('1',ip=input("ip > ")or"localhost",port=12412,start_on_connect=False)
    serv.to_run = cpu
    a = Process(target=serv.open)
    a.start()

    input("Press enter to run all clients\n")
    serv.args_parall = serv.divide_threads([(50000000*i,50000000*(i+1)) for i in range(10)])
    serv.run_parall()
    
    input("Press enter to finish\n")

    print(serv.result)

def cpu(f,t):
    b = 0
    for a in range(f,t):
        b += a
    return b

### This class is a proof of concept
class RPC(rpyc.Service):
    def __init__(self, identifier:str, ip:str="localhost", port:int=0, server:"Server"=None,
                *,start_on_connect:bool=True, self_parall:bool=True):
        print("RPC.__init__")
        self.ip = str(ip)
        self.port = int(port)

        self.server = server

        if(server is None): self._manager = Manager()
        else: self._manager = server._manager

        self._clients = External_list()
        self.__client_num = None

        self.client_start = []
        self.default_start = start_on_connect

        self.client_threads = self._manager.list()

        self.identifier = identifier

        self._socket = None

        self._run = None
        self._run_parall = None

        self._to_run = None

        self._args = []
        self._args_per_client = None
        self._args_parall = []

        self._result = External_list()

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

    def on_disconnect(self, _):
        self._clients.remove(self)
        for obj in self._clients:
            obj._set_client_num()

    def exposed_set_threads(self, threads:int):
        self.client_threads[self.__client_num] = threads
        print(f"Client {self.__client_num} has {threads} threads")

    def exposed_set_run(self, run_funct, run_parall=None):
        self._run = run_funct
        self._run_parall = run_parall

    def exposed_run_run(self):
        if(self._run is None): return -1
        
        run = rpyc.async_(self._run)
        self._result.append(run)

        if(self._args_per_client is None): 
            future = run(self.to_run, *self._args)
        else:
            future = run(self.to_run, *self._args_per_client[self.__client_num])

        return future

    def exposed_run_parall(self):
        if(self._run_parall is None): return -1

        future = rpyc.async_(self._run_parall)(self.to_run, self.args_parall[self.__client_num])
        self._result.append(future)

        return future


    def run(self):
        for obj in self._clients:
            obj.exposed_run_run()

    def run_parall(self):
        for obj in self._clients:
            obj.exposed_run_parall()


    def result_async_values(self):
        result = []
        for num,result_end in enumerate(self._result):
            if(hasattr(result_end,"ready")):
                if(result_end.ready):
                    self._result[num] = result_end.value
                    result.append(result_end.value)
                continue
            
            result.append(result_end)
        
        return result

    def exposed_result_async(self):
        self.result_async_values()

    def divide_eq(self, iterable, n=None, fill=None):
        if(n is None): n = ceil(len(iterable) / sum(self.client_threads))
        return zip_longest(*[iter(iterable)]*n, fillvalue=fill)

    def divide_threads(self, iterable):
        prev = 0
        result = [] 
        for thread in self.client_threads:
            if(prev >= len(iterable)): break

            result.append(iterable[prev:prev+thread])
            prev += thread

        print(f"divide_threads : {result}")

        return result

    def _set_client_num(self):
        self.__client_num = self._clients.index(self)

    def get_to_run(self):
        return self._to_run
    def set_to_run(self, new_to_run):
        self._to_run = export_function(new_to_run)
        
        for obj in self._clients:
            obj._to_run = self._to_run

    def get_args(self):
        return self._args
    def set_args(self, new_args):
        self._args = new_args

        for obj in self._clients:
            obj._args = self._args
                
    def get_args_per_client(self):
        return self._args_per_client
    def set_args_per_client(self, new_args_pc):
        self._args_per_client = new_args_pc

        for obj in self._clients:
            obj._args_per_client = self._args_per_client

    def get_args_parall(self):
        return self._args_parall
    def set_args_parall(self, new_args_parall):
        self._args_parall = new_args_parall

        for obj in self._clients:
            obj._args_parall = self._args_parall

    to_run = property(get_to_run, set_to_run)
    args = property(get_args,set_args)
    args_per_client = property(get_args_per_client,set_args)
    args_parall = property(get_args_parall,set_args_parall)
    result = property(result_async_values)

class External_list(list):
    def __init__(self, iterable=[]):
        super().extend(iterable)



if __name__ == "__main__":
    main()
else: print("Imported RPC Server")