import socket
import logging
import time, datetime
#import wmi
import psutil, platform
from re import finditer
from Languages.Server_lang import lang
from multiprocessing import Manager

try:
    import Server
except ImportError: pass

def main():
    import sys
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.DEBUG)
    cl = Client({})
    ip = input("ip: ")
    port = input("port: ")
    cl.connect(ip if ip else 'localhost', 
                port if port else 12412)

    #1st ping
    print("listen1")
    cl.data_parse(next(cl.listener))

    #recon
    print("listen2")
    cl.data_parse(next(cl.listener))

    #2nd ping
    print("listen3")
    cl.data_parse(next(cl.listener))

class Client():
    def __init__(self, ip:str="localhost", port:int=12412, order_dict:dict={}):
        logging.debug(f"Client.__init__(self)")
        logging.info("Created new client")
        self.listener = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip = ip
        self.port = port

        self.order_dict = {**order_dict,
                "--_ping":self.ping,"--_recon":self.change_server
                }

        self.conn_step = [lang.Serv_to_Client]

        self.__manager = Manager()
     
        try:
            Server.Process(target=lambda x: x, args=(1))
            self.__can_be_server = True 
        except Exception:
            self.__can_be_server = False

        self.next_server = self.__manager.list()

    def connect(self, ip:str=None, port:int=None):
        if(ip is None): ip = self.ip
        if(port is None): port = self.port
        logging.debug(f"Client.connect(self, {ip}, {port})")

        if(not self.listener is None): socket_to = self.__server_aux
        else: socket_to = self.server

        while(True):
            try:
                socket_to.connect((ip, int(port)))
                break
            except ConnectionRefusedError: pass

        logging.info(f"Connected to server in {ip}:{port}")

        # later i will keep it until self.server is closed
        self.listener = self.listen(socket_to)

        return self.listener

    def change_server(self, ip:str, port:int): 
        self.connect(ip, port)

        print("Connected")
        
        self.server.close()

        print("Closed")

        self.server,self.__server_aux = self.__server_aux,socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def send_sys_info(self):
        self.send_to_server({
                "ram":psutil.virtual_memory().total,
                "cpu":platform.processor(),
                "os":platform.architecture()})

    def listen(self, server:socket.socket) -> "generator":
        timeout = 0
  
        while(True):
            data = server.recv(1024)
            decoded_data = data.decode("utf-8")

            if(data is None):
                timeout += 1
                if(timeout > 9): break
            elif(decoded_data != ''):
                timeout = 0
                del data
                yield decoded_data

    def send_to_server(self, data:str):
        if(not self.server is None):
            self.server.sendall(bytes(str(data), "utf-8"))
    
    def data_parse(self, data:str):
        #print(f"data_parse {data}")
        order = None
        args = ()
        for arg in data.split(lang.Divider):
            new_ord = self.order_dict.get(arg.strip(), None)
            print(f"arg:{arg}, new_ord:{new_ord}")
            if(not new_ord is None):
                if(not order is None): 
                    print(f"{order}{args}")
                    try:
                        order(*args)
                    except Exception as err: print(f"ERROR: {err}")
                    
                order = new_ord
                args = ()
                
            elif(arg.strip() != '' and not arg.strip().startswith(lang.Comment)): args+=(arg.strip(),)
            
        if(not order is None): 
            print(f"{order}{args}.")
            try:
                order(*args)
            except Exception as err:
                print(order)
                print(args)
                raise err
                print(f"ERROR: {err}.")

    def symbol_parse(self, command:str):
        urgent = False
        num = 0 
        for symbol in finditer('|'.join(lang.values()), command):
            if(symbol.group(0) == lang.Urgency):
                urgent = True
            else:
                if(urgent):
                    self.conn_step.insert(0, symbol.group(0))
                    urgent = False
                    num += 1
                else:
                    self.conn_step.append(symbol.group(0))
      

    def ping(self):
        self.send_to_server("/-/"+"0"*972)

if __name__ == "__main__":
    main()