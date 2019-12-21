import socket
import logging
import time, datetime
import rpyc
import psutil, platform
from re import finditer
from Languages.Server_lang import lang
from multiprocessing import Manager
from Clients import *

from os import listdir
from collections import defaultdict

try:
    import Server
except ImportError: pass

def main():
    import sys
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)

    ip = input("ip: ") or "127.0.0.1"
    port = input("port: ") or 12412
    protocol = input("protocol: ") or "RPC"

    cl = Client(ip, port, {}, protocol=protocol)
    cl.open()

    conn = cl.server.server
    s = cl.server

    conn.serve_all()


class Client():
    def __init__(self, ip:str="localhost", port:int=12412, order_dict:dict={}, protocol="TCP"):
        logging.debug(f"Client.__init__(self)")
        logging.info("Created new client")
        self.listener = None

        self.protocol = protocol.upper()

        self.__clients_const_by_str = dict([[mod[:-3],eval(f"{mod[:-3]}.{mod[:-3]}")] for mod in listdir(f"{__file__[:-9]}Clients") if mod[-3:] == '.py' and mod != "__init__.py"])

        self.ip = str(ip)
        self.port = int(port)

        self.order_dict = {**order_dict,
                "--_ping":self.ping,"--_recon":self.change_server
                }

        self.server = self.__clients_const_by_str[protocol](ip=self.ip, port=self.port, 
                                                            order_dict=self.order_dict)

        self.conn_step = [lang.Serv_to_Client]

        self.__manager = Manager()

        try:
            Server.Process(target=lambda x: x, args=(1))
            self.__can_be_server = True 
        except Exception:
            self.__can_be_server = False

        self.next_server = self.__manager.list()

    def __enter__(self):
        self.open()

    def __exit__(self,_,__,___):
        self.close()

    def open(self):
        self.server.open()

    def close(self):
        self.server.close()

    def change_server(self, ip:str, port:int): 
        self.server.change_server(ip,port)

    def ping(self):
        self.server.ping()


if __name__ == "__main__":
    main()
