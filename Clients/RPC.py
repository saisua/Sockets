import rpyc
from rpyc.utils.teleportation import import_function
from rpyc.utils.helpers import BgServingThread

import logging
from multiprocessing import cpu_count, Manager
import sys

#sys.path.append(sys.path[0][:-7])

from concurrent.futures import ProcessPoolExecutor, wait

def main():
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)

    ip = input("ip: ") or "127.0.0.1"
    port = input("port: ") or 12412

    RPC(ip, port)

class RPC(rpyc.Service):
    def __init__(self, ip:str="localhost", port:int=12412, order_dict:dict={},
                    *, max_timeout=600, keepalive:bool=True, keep_background:bool=True):
        logging.debug(f"RPC.__init__(self)")
        logging.info("new RPC client")

        self.listen = False

        self.ip = ip
        self.port = port

        self.order_dict = {**order_dict,
                "--_ping":self.ping,"--_recon":self.change_server
                }

        self.max_timeout = max_timeout
        self.keepalive = keepalive

        self.keep_background = keep_background

        self.__threads = cpu_count()

        self._manager = Manager()

    def __enter__(self):
        self.open()

    def __exit__(self,_,__,___):
        self.close()

    def open(self):
        print("RPC.open(self)")
        while(True):
            try:
                self.server = rpyc.connect(self.ip, self.port, service=self, 
                                            keepalive=self.keepalive)
                break
            except ConnectionRefusedError: pass

        if(self.keep_background): self.keep_background = BgServingThread(self.server)

        self.server.SYNC_REQUEST_TIMEOUT = self.max_timeout
        self.server.root.set_threads(self.__threads)
        self.server.root.set_run(self.run, self.run_parall)

        self.listen = True
        #self.server.root.run_parall()
        print("Connected to the server")

    def close(self):
        self.server.close()

    def ping(self):
        pass

    def change_server(self, ip:str, port:int):
        pass

    def run(self, funct, *args, **kwargs):
        print("RPC.run")
        self.listen = False

        result = import_function(funct)(*args, **kwargs)

        self.listen = True

        return result

    def run_parall(self, funct, args):
        print("RPC.run_parall")
        self.listen = False

        futures = []
        funct = import_function(funct)

        print(f"Running a pool of {self.__threads} process")
        with ProcessPoolExecutor(self.__threads) as executor:
            for arg in args:
                futures.append(executor.submit(funct, *arg))

            executor.shutdown()

        print("Done")

        self.listen = True

        return [future.result() for future in futures]

if __name__ == "__main__":
    main()
else: print("Imported RPC (client)")