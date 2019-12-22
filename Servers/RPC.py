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
from datetime import datetime

def main():
    from operator import attrgetter
    serv = RPC ('1',ip=input("ip > ")or"localhost",port=12412,start_on_connect=False)
    serv.to_run = cpu
    serv.args_parall = [[(0, 50000000), (50000000, 100000000), (100000000, 150000000), (150000000, 200000000), (200000000, 250000000), (250000000, 300000000), (300000000, 350000000), (350000000, 400000000)]]
    a = Process(target=serv.open)
    a.start()

    i = 1
    input("Press enter to run all clients\n")
    bef = datetime.now()
    
    while(i):
        serv.args_parall = serv.divide_threads([(50000000*i,50000000*(i+1)) for i in range(22)])
        #serv.args_per_client = [(50000000*i,50000000*(i+1)) for i in range(10)]
        serv.run_parall()
        print(serv._clients)
        
        i=False #input("Press enter to stop running all clients\n")

    while(not all(map(attrgetter("ready"), serv._result))): time.sleep(.5)
    tim = datetime.now()-bef
    #input("Press enter to finish\n")

    res = RPC.flatten(serv.result)
    print(res)
    print("\n\nResult:")
    print(sum(res))
    print(f"\nJob ended in {tim.total_seconds()} seconds")

    exit(0)

def cpu(f,t):
    b = 0
    for a in range(f,t):
        b += a

    return b


### This class is a proof of concept
class RPC(rpyc.Service):
    def __init__(self, identifier:str, ip:str="localhost", port:int=0, server:"Server"=None,
                *,start_on_connect:bool=True, self_parall:bool=True, max_timeout:int=600):
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

        self._run = []
        self._run_parall = []

        self._to_run = None

        self._args = []
        self._args_per_client = None
        self._args_parall = []

        self._result = External_list()

        self.max_timeout = max_timeout

    # Shared functions
   
    def __enter__(self):
        self.open()

    def __exit__(self,_,__,___):
        pass

    def open(self):
        self._socket = ThreadedServer(self, hostname=self.ip, port=self.port)
        self._socket.SYNC_REQUEST_TIMEOUT = self.max_timeout

        self._socket.start()
        print(f"Open server ({self._socket}) in \n{self.ip}:{self.port}")

    def on_connect(self, conn):
        self._clients.append(conn)
        
        print(f"New client {len(self._clients)} connected")
        return super().on_connect(conn)

    def on_disconnect(self, conn):
        index = self._clients.index(conn)
        self._clients.pop(index)
        self._run.pop(index)
        self._run_parall.pop(index)
        self.client_threads.pop(index)

    def exposed_set_threads(self, threads:int):
        self.client_threads.append(threads)
        print(f"New client {len(self._clients)} has {threads} threads")

    def exposed_set_run(self, run_funct, run_parall=None):
        self._run.append(run_funct)
        self._run_parall.append(run_parall)

    def exposed_run_run(self, client:int=0):
        if(self._run is None): return -1

        if(client >= 0):
            run = rpyc.async_(self._run[client])
        
            if(self._args_per_client is None): 
                future = run(self.to_run, *self._args)
            else:
                future = run(self.to_run, *self._args_per_client[self.__client_num])

            self._result.append(future)
        else:
            for num, run in enumerate(self._run):
                run = rpyc.async_(run)
        
                if(self._args_per_client is None): 
                    future = run(self.to_run, *self._args)
                else:
                    future = run(self.to_run, *self._args_per_client[num])

                self._result.append(future)

        return future

    def exposed_run_parall(self):
        if(self._run_parall is None): return -1

        for num, run in enumerate(self._run_parall):
            print(run)
            run = rpyc.async_(run) # In a var, as asked in the docs

            future = run(self.to_run, self.args_parall[num])
            self._result.append(future)
    


    def run(self, client:int=0):
        self.exposed_run_run(client)

    def run_parall(self):
        self.exposed_run_parall()

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

    def get_args(self):
        return self._args
    def set_args(self, new_args):
        self._args = new_args
                
    def get_args_per_client(self):
        return self._args_per_client
    def set_args_per_client(self, new_args_pc):
        self._args_per_client = new_args_pc

    def get_args_parall(self):
        return self._args_parall
    def set_args_parall(self, new_args_parall):
        self._args_parall = new_args_parall
        

    to_run = property(get_to_run, set_to_run)
    args = property(get_args,set_args)
    args_per_client = property(get_args_per_client,set_args_per_client)
    args_parall = property(get_args_parall,set_args_parall)
    result = property(result_async_values)

    @staticmethod
    def flatten(l):
        result = []
        for level in l:
            if(isinstance(level, Iterable)):
                result.extend(level)
            else:
                result.append(level)
        return result
                

class External_list(list):
    def __init__(self, iterable=[]):
        super().extend(iterable)



if __name__ == "__main__":
    main()
