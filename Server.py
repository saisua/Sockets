import socket, logging, datetime
import xmlrpc
from multiprocessing import Process, Manager
from Servers import *
from os import listdir

def main():
    serv = Server()
    tcp = serv.open('TCP','')
    serv.test(tcp)
    
class Server():
    def __init__(self, ip:str=None, port:tuple=12412, max_connections:int=-1,
                        order_dict:dict={}, listen_timeout:float=30, threaded:bool=True,
                        servers:"dict['Serv_type':['Listen','Send']"={'TCP':['Send']}):
        logging.debug(f"Server.__init__(self, {ip}, {port}, {max_connections})")
        self.threaded = threaded
        
        self.__manager = Manager()
        self._client_from_addr = self.__manager.dict()
        self._process_from_addr = {}
        self.__open = self.__manager.dict()
        
        self.order_dict = {**order_dict}
        self.next_server = self.__manager.list()

        self.servers = self.__manager.dict(servers)
        self.__servers = {}
        self.__servers_by_str = dict([[mod[:-3],eval(f"{mod[:-3]}.{mod[:-3]}")] for mod in listdir(f"{__file__[:-9]}Servers") if mod[-3:] == '.py'][:-1])

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
        logging.info("Created new server manager")

    def open(self, server_type:str, started_in:str):
        return self.__servers_by_str[server_type]()
        
    def test(self,serv):
        print(f"port:{serv.port}")
        addr = serv.open()
        listener = serv.create_listener(addr,
                        serv._client_from_addr[addr])
        messages = next(listener)
        while(messages and messages != '\r\n'): 
            print(f"Recieved {messages}")
            serv.sendto(messages,addr)
            messages = next(listener)
        print('hi')
        serv.join()
        print('wsup')
        serv.close()

        print("byee")

if __name__ == "__main__":
    main()