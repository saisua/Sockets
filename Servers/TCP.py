import socket
from multithr import Process
from Languages.Server_lang import lang

def main():
    with TCP() as serv:
        pass

class TCP():
    def __init__(self, ip:str="localhost", port:int=0, server:"Server"=None, *, 
                        locks:tuple=(), max_clients:int=1):
        self.ip = str(ip)
        self.port = int(port)

        self._server = server
        self._manager = server.__manager if not server is None else None

        self.locks = locks

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self.ip, self.port))
        self.port = self._socket.getsockname()[1]

        self.max_clients = int(max_clients)
        self._client_from_addr = {}

        self.__open = {'':False}

        self.open_processes = []

        self.__test = True

    def __del__(self):
        self.close()

    # Shared functions

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _, __, ___):
        self.close()

    def open(self):
        self.__open[''] = True
        if(self.__test): return self.listen_connections(1,self.ip,self.port)
        else:
            open_process = Process(target=self.listen_max_conn, args=(self.ip,self.port), daemon=True)
            self.open_processes.append(open_process)
            open_process.start()

    def close(self):
        self.__open[''] = False

        self.join()
        self._socket.close()

    def join(self):
        for proc in self.open_processes: proc.join()

    def ping(self, addr:tuple, send_time:str=None) -> None:
        if(send_time is None):
            self.client.sendto("--_ping",addr)
            self.listen(addr)

    # TCP functions

    def listen_max_conn(self, ip:str=None, port:int=None):
        while(len(self._client_from_addr) < self.max_clients):
            remaining = self.max_clients-len(self._client_from_addr)
            self.listen_connections(2 if remaining>1 else remaining, ip, port)

    def listen_connections(self, connections:int=1, ip:str=None, port:int=None):
        if(not self.__open['']): return
        
        if(self.__test): return self.new_connection(ip, port)
        else:
            process = [] 
            for _ in range(connections):
                process.append(Process(target=self.new_connection, args=(ip, port)))
                
                process[-1].start()
                
            for conn in process: conn.join()
    
    def new_connection(self, ip:str=None, port:int=None):
        if(self.max_clients + 1 and len(self._client_from_addr) >= self.max_clients): return
        if(not self.__open['']): return
    
        if(ip is None): ip = self.ip
        if(port is None): port = self.port

        self._socket.listen()
            
        listener, addr = self._socket.accept()
        
        self._client_from_addr[addr] = listener
        self.__open[addr] = True

        if(self.__test): return addr

    def sendto(self, message:str, addr:tuple):
        self._client_from_addr[addr].sendto(bytes(str(message), "utf-8"), addr)

    def sendall(self, message:str):
        self._socket.sendall(bytes(str(message), "utf-8"))
    
    def create_listener(self, addr, listener):
        if(self.__open[''] and not self.__open[addr]): return
        
        with listener:
            timeout = 0
            while(self.__open[''] and self.__open[addr]):
                #lock.acquire()
                data = listener.recv(1024)
                decoded_data = data.decode("utf-8")

                if(data is None):
                    timeout += 1
                    #logging.debug(f"Timeout of user {addr} increased to {timeout}")
                    if(timeout > 9): 
                        #logging.warning(f"User {addr} has disconnected")
                        break
                elif(decoded_data != ''):
                    timeout = 0
                    #logging.info(f"Recived data '{decoded_data}' from address {addr}")
                    
                    yield decoded_data

        del self._process_from_addr[addr]
        del self._client_from_addr[addr]
        del self.__open[addr]
                                            
    def parse_data(self, data:str, addr:str):
        #print(f"parse_data {data}")
        order = None
        args = (addr,)
        for arg in data.split(';'):
            new_ord = self.order_dict.get(arg.strip(), None)
            print(f"arg:{arg}, new_ord:{new_ord}")
            if(not new_ord is None):
                if(not order is None): 
                    print(f"{order}{args}")
                    try:
                        order(*args)
                    except Exception as err: print("ERROR: {err}")
                    
                order = new_ord
                args = (addr,)
                
            elif(arg.strip() != ''): args+=(arg.strip(),)
            
        if(not order is None): 
            print(f"{order}{args}.")
            try:
                order(*args)
            except Exception as err: print(f"ERROR: {err}")

if __name__ == "__main__":
    main()
else: print("Imported TCP Server")