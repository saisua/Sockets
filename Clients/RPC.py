import rpyc
from rpyc.utils.teleportation import import_function
import logging


def main():
    import sys
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)

    ip = input("ip: ") or "127.0.0.1"
    port = input("port: ") or 12412
    protocol = input("protocol: ") or "RPC"

    cl = RPC(ip, port, {}, protocol=protocol)

class RPC(rpyc.Service):
    def __init__(self, ip:str="localhost", port:int=12412, order_dict:dict={}):
        logging.debug(f"RPC.__init__(self)")
        logging.info("new RPC client")

        self.listener = None

        self.ip = ip
        self.port = port

        self.order_dict = {**order_dict,
                "--_ping":self.ping,"--_recon":self.change_server
                }

    def __enter__(self):
        self.open()

    def __exit__(self):
        self.close()

    def open(self):
        while(True):
            try:
                self.server = rpyc.connect(self.ip, self.port, service=self)
                break
            except ConnectionRefusedError: pass
        
        print("Trying to run :P")
        print(dir(self.server.root))
        self.server.root.set_run(self.run)

        self.server.root.run_run()
        print("Done")

    def close(self):
        self.server.close()

    def ping(self):
        pass

    def change_server(self, ip:str, port:int):
        pass

    def run(self, funct, *args, **kwargs):
        return import_function(funct)(*args, **kwargs)

if __name__ == "__main__":
    main()
else: print("Imported RPC (client)")