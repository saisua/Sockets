import rpyc
from rpyc.utils.teleportation import import_function
import logging
from multiprocessing import cpu_count
import sys

#sys.path.append(sys.path[0][:-7])

from multithr import Process 

def main():
    import sys
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)

    ip = input("ip: ") or "127.0.0.1"
    port = input("port: ") or 12412

    RPC(ip, port)

class RPC(rpyc.Service):
    def __init__(self, ip:str="localhost", port:int=12412, order_dict:dict={},
                    *, max_timeout=600, keepalive:bool=True):
        logging.debug(f"RPC.__init__(self)")
        logging.info("new RPC client")

        self.listener = None

        self.ip = ip
        self.port = port

        self.order_dict = {**order_dict,
                "--_ping":self.ping,"--_recon":self.change_server
                }

        self.max_timeout = max_timeout
        self.keepalive = keepalive

        self.__threads = cpu_count()

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

        self.server.SYNC_REQUEST_TIMEOUT = self.max_timeout
        self.server.root.set_threads(self.__threads)
        self.server.root.set_run(self.run, self.run_parall)
        #self.server.root.run_run()
        print("Connected to the server")

    def close(self):
        self.server.close()

    def ping(self):
        pass

    def change_server(self, ip:str, port:int):
        pass

    def run(self, funct, *args, **kwargs):
        print("RPC.run")
        return import_function(funct)(*args, **kwargs)

    def run_parall(self, funct, *args):
        print("RPC.run_parall")
        procs = []
        funct = import_function(funct)
        for arg in args:
            procs.append(Process(target=funct, args=arg))
            procs[-1].start()

        for proc in procs: proc.join()

        return [p._tmp_result for p in procs]

if __name__ == "__main__":
    main()
else: print("Imported RPC (client)")