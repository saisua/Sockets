import socket
import logging
import time, datetime
#import wmi
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
    listener = cl.connect(ip if ip else 'localhost', 
                port if port else 12412)

    messages = input("Send:\n> ")
    while(messages and messages != '\r\n'):
        cl.send_to_server(messages)
        print(next(listener))
        messages = input("> ")

class Client():
    def __init__(self, order_dict:dict):
        logging.debug(f"Client.__init__(self)")
        logging.info("Created new client")
        self.listener = None
        self.server = None

        self.order_dict = order_dict

        self.conn_step = [lang.Serv_to_Client]

        self.__manager = Manager()
     
        try:
            Server.Process(target=lambda x: x, args=(1))
            self.__can_be_server = True 
        except Exception:
            self.__can_be_server = False

        self.next_server = self.__manager.list()

    def connect(self, ip:str, port:int=12412):
        logging.debug(f"Client.connect(self, {ip}, {port})")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while(True):
            try:
                server.connect((ip, int(port)))
                break
            except ConnectionRefusedError: pass

        self.server = server
        logging.info(f"Connected to personal port in {ip}:{port}")

        self.listener = self.listen(server)

        return self.listener

    def listen(self, server:socket.socket) -> "generator":
        timeout = 0
        
        #server.settimeout(10)

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
        for arg in data.split(lang.Divisor):
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
                
            elif(arg.strip() != ''): args+=(arg.strip(),)
            
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
        for symbol in finditer('|'.join(self.conn_symbols.values()), command):
            if(symbol.group(0) == self.lang.Urgency):
                urgent = True
            else:
                if(urgent):
                    self.conn_step.insert(0, symbol.group(0))
                    urgent = False
                    num += 1
                else:
                    self.conn_step.append(symbol.group(0))
      

    def ping(self):
        self.send_to_server(datetime.datetime.now())

if __name__ == "__main__":
    main()