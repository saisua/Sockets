import socket, logging, datetime
import xmlrpc
from multiprocessing import Process, Manager
from Servers import *

def main():
    logging.error("This file should not be executed directly")
    
class Server():
    def __init__(self, ip:str=None, port:tuple[int]=(12412,), max_connections:int=-1,
                        order_dict:dict={}, listen_timeout:float=30, threaded:bool=True,
                        servers:dict["TCP":["Listen","Send"], 
                        "UDP":["Listen","Send"], "RCP":["Listen","Send"]]={"TCP":["Send"],"UDP":[],"RCP":[]}):
        logging.debug(f"Server.__init__(self, {ip}, {port}, {max_connections})")
        self.threaded = threaded
        
        self.__manager = Manager()
        self._client_from_addr = self.__manager.dict()
        self._process_from_addr = {}
        self.open = self.__manager.dict()
        
        self.order_dict = {**order_dict, "--_ping":self.ping}
        self.next_server = self.__manager.list()

        self.servers = self.__manager.dict(servers)

        self.clients_new_server = self.__manager.dict()

        if(ip is None): 
            ip = socket.gethostbyname_ex(socket.gethostname())[-1]
            if(type(ip) is list or type(ip) is tuple): ip = ip[-1]
            logging.warning(f"Ip set automatically to {ip}")

            ip = "127.0.0.1"
            logging.warning(f"Ip set automatically to {ip}")

        self.ip = ip
        self.port = int(port)

        self.max_connections = int(max_connections) if max_connections >= -1 else -1

        self._connection = socket.socket(socket.AF_INET, 
                            socket.SOCK_STREAM)
        self._connection.bind((ip, port))

        self.listen_timeout = listen_timeout
        logging.info("Created new server")

        