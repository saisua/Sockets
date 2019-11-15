import socket, logging, datetime
import xmlrpc
from multiprocessing import Process, Manager
from Servers import *
from os import listdir
from collections import defaultdict

def main():
    serv = Server(servers={"TCP":["Send"]})
    with serv as new_server: 
        serv.test(new_server[1]["TCP"][0])
    
class Server(): 
    def __init__(self, ip:str=None, port:tuple=12412, max_connections:int=-1,
                        order_dict:dict={}, listen_timeout:float=30, threaded:bool=True,
                        servers:"dict['Serv_type':['Listen','Send']"={'TCP':['Send']}):
        logging.debug(f"Server.__init__(self, {ip}, {port}, {max_connections})")
        self.threaded = threaded
        
        self._manager = Manager()
        self._process_from_serv = {}
        self.__open = self._manager.dict()
        
        self.order_dict = {**order_dict}
        self.next_server = self._manager.list()

        self.servers = self._manager.dict(servers)
        self.servers_len = lambda serv: sum([len(state) for _,state in serv.items()])
        self.__servers = defaultdict(lambda : [])
        self.__servers_by_str = dict([[mod[:-3],eval(f"{mod[:-3]}.{mod[:-3]}")] for mod in listdir(f"{__file__[:-9]}Servers") if mod[-3:] == '.py'][:-1])

        self.clients_new_server = self._manager.dict()

        if(self.servers_len(self.__servers) > 1):
            self.router_server = TCP.TCP(ip, port, self, max_clients=-1)
        else: self.router_server = None

        if(ip is None): 
            ip = socket.gethostbyname_ex(socket.gethostname())[-1]
            if(type(ip) is list or type(ip) is tuple): ip = ip[-1]
            logging.warning(f"Ip set automatically to {ip}")

            ip = "127.0.0.1"
            logging.warning(f"Ip set automatically to {ip}")

        self.ip = ip
        self.port = int(port)

        self.max_connections = int(max_connections) if max_connections >= -1 else -1

        self.listen_timeout = listen_timeout
        logging.info("Created new server manager")

    def __enter__(self):
        return self, self.open_all()

    def __exit__(self, _, __, ___):
        for sock_type, server_list in self.__servers.items():
            for server in server_list:
                server.close()

    def open(self, server_type:str, started_in:str):
        if(self.servers_len(self.servers) == 1 and 
                self.servers_len(self.__servers) == 1): 
            self.__servers.values()[0][0].bind_to(ip=self.ip)

        if(self.servers.get(server_type, None) is None): 
            self.servers[server_type] = [started_in]
        elif(len([None for serv in self.__servers[server_type] if serv.state == started_in]) 
                    >= self.servers[server_type].count(started_in)):
            self.servers[server_type].append(started_in)   

        new_server = self.__servers_by_str[server_type](ip=self.ip, 
                            port = self.port if self.servers_len(self.servers) == 1 else 0,    
                            server=self, state=started_in)

        self._process_from_serv[new_server] = Process(target=new_server.open, daemon=True)
        
        self.__servers[server_type].append(new_server)
        return new_server
        
    def open_all(self):
        for sock_type, state_list in self.servers.items():
            for state in state_list:
                new_server = self.open(sock_type, state)
                print(f"Opened new {sock_type} server in {new_server.port}")

        return self.__servers        

    def test(self,serv):
        print(f"port:{serv.port}")
        time = serv.open()
        print(f"Ping time: {time}")
        print('hi')
        serv.join()
        print('wsup')
        serv.close()

        print("byee")

if __name__ == "__main__":
    main()