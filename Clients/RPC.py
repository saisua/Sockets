import rpyc

from rpyc.utils.teleportation import import_function

from rpyc.utils.helpers import BgServingThread

from multiprocessing import cpu_count, Manager, Process

#sys.path.append(sys.path[0][:-7])

def main():
    #logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)

    ip = input("ip: ") or "127.0.0.1"
    port = input("port: ") or 12412

    RPC(ip, port)

class RPC(rpyc.Service):
    def __init__(self, ip:str="localhost", port:int=12412, order_dict:dict={},
                    *, max_timeout=600, keepalive:bool=True, keep_background:bool=True,
                     max_threads:int=None):
        print(f"RPC.__init__(self)")
        print("new RPC client")

        self.ip = ip
        self.port = port

        self.order_dict = {**order_dict,
                "--_ping":self.ping,"--_recon":self.change_server
                }

        self.max_timeout = max_timeout
        self.keepalive = keepalive

        self.keep_background = keep_background

        self.__threads = max_threads or cpu_count()

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

        result = import_function(funct)(*args, **kwargs)

        return result

    def run_parall(self, funct, args):
        print("RPC.run_parall")

        futures = self._manager.list()
        procs = []

        print(f"Running a pool of {len(args)} process")
  #      with self._executor as executor:
            
        for arg in args:
            p = Process(target=run_proc, args=(funct,arg,futures),daemon=True)
            procs.append(p)
            p.start()

        for proc in procs: proc.join()

        print("Done")
        
        return list(futures)

def run_proc(funct_bin, arg, futures):
        print("| Start Thread")
        funct = import_function(funct_bin)
        futures.append(funct(*arg))
        print("+ Thread ended")

if __name__ == "__main__":
    main()
