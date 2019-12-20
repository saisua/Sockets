import socket, logging, datetime
import rpyc
from multiprocessing import Process, Manager
from Servers import *
from os import listdir
from collections import defaultdict
from time import sleep

def main():
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)
    serv = Server(servers={"RPC":['1']})
    serv._servers_by_id['1'].to_run = cpu
    serv.open_all()

    print(serv._servers_by_id)
    
    while(True): sleep(1)
   

def cpu():
    b = 0
    for a in range(50000000):
        b += a
    return b
    
class Server(): 
    def __init__(self, ip:str=None, port:tuple=12412, max_connections:int=-1,
                        order_dict:dict={}, listen_timeout:float=30, threaded:bool=True,
                        servers:"dict['Serv_type':['Identifiers',]]"={'TCP':['Test']}):
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
        self._servers_by_id = {}
        
        self.__servers_const_by_str = dict([[mod[:-3],eval(f"{mod[:-3]}.{mod[:-3]}")] for mod in listdir(f"{__file__[:-9]}Servers") if mod[-3:] == '.py' and mod != "__init__.py"])
        # I know the line above is far from good, but it was the easy way and it will only be execute once

        self.clients_new_server = self._manager.dict()

        if(ip is None): 
            ip = socket.gethostbyname_ex(socket.gethostname())[-1]
            if(type(ip) is list or type(ip) is tuple): ip = ip[-1]

            ip = "127.0.0.1"
            logging.warning(f"Ip set automatically to {ip}")

        self.ip = ip
        self.port = int(port)

        if(self.servers_len(self.servers) > 1):
            self.router_server = self.create_router_serv()
        else: self.router_server = None

        self.max_connections = int(max_connections) if max_connections >= -1 else -1

        self.listen_timeout = listen_timeout

        for server_type,id_list in servers.items():
            for identifier in id_list:
                self.create_server(server_type, identifier)

        logging.info("Created new server manager")

    def __enter__(self):
        return self, self.open_all()

    def __exit__(self, _, __, ___):
        for _, server_list in self.__servers.items():
            for server in server_list:
                server.close()

    def create_server(self, server_type:str, identifier:str=None, *, force=False):
        if(self.__servers_const_by_str.get(server_type, None) is None): 
            print(self.__servers_const_by_str)
            raise Exception(f"Server constructor file {server_type}.py not found. Check the input given")
        
        if(identifier is None): 
            id_num = len(self._servers_by_id)
            identifier = f"{server_type}{id_num}"

            # Just in case
            while(identifier in self._servers_by_id.keys()):
                id_num += 1
                identifier = f"{server_type}{id_num}"

            del id_num
        
        if(not force and self.servers_len(self.servers) == 1 and 
                        self.servers_len(self.__servers) == 1): 
            first_serv = list(self.__servers.values())[0][0]
            stype = self.servers.keys()[0]
            sid = self.servers.values()[0][0]
            new_serv = self.create_server(stype, sid, force=True)
            self._process_from_serv[new_serv] = Process(target=new_serv.open, daemon=True)
            self._process_from_serv[new_serv].start()

            first_serv.bind_to(ip=self.ip, port=new_serv.port)

            print(f"Moved first server to {self.ip}:{first_serv.port}")

            self.router_server = self.create_router_serv()

            Process(target=first_serv.close, daemon=True)
            #del self._process_from_serv[first_serv]
            self.__servers[stype].remove(first_serv)
            # To-do: create self.close()

            del first_serv, new_serv, stype, sid

        new_server =  self.__servers_const_by_str[server_type](ip=self.ip, 
                            port = self.port if identifier == "_router_" or 
                                            (self.servers_len(self.servers) < 2 and
                                            not len(self._servers_by_id)) else self.__get_open_port(),    
                            server=self, identifier=identifier)

        self.__servers[server_type].append(new_server)
        
        if(self.servers.get(server_type, None) is None): self.servers[server_type] = [identifier]
        elif(self._servers_by_id.get(identifier,None) is None):
            self.servers[server_type] = self.servers[server_type]+[identifier]
        
        self._servers_by_id[identifier] = new_server

        return new_server   

    def open(self, server_type:str, identifier:str=None, *, force=False):
        new_server = self._servers_by_id.get(identifier, None)
        if(new_server is None): new_server = self.create_server(server_type, identifier, force=force)

        self._process_from_serv[new_server] = Process(target=new_server.open, daemon=True)
        self._process_from_serv[new_server].start()
        
        return new_server
        
    def open_all(self, *, force=False):
        for sock_type, id_list in self.servers.items():
            for id_ in id_list:
                by_id = self._servers_by_id.get(id_, None)
                if by_id is None and not by_id._open['']:
                    new_server = self.open(sock_type, id_, force=force)
                    print(f"Opened new {sock_type} server in {new_server.port}")

        return self.__servers        

    def create_router_serv(self):
        return self.create_server("TCP","_router_",force=True)

    def __get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, 0))
        p = s.getsockname()[1]
        s.close()
        return p

    def test(self,serv):
        print(f"port:{serv.port}")
        print(serv.open())

        print("byee")

if __name__ == "__main__":
    main()
