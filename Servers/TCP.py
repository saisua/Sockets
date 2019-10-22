import socket
from multiprocessing import Manager

def main():
    pass

class TCP():
    def __init__(self, ip:str="localhost", port:int=12412, locks:tuple["Lock"]=()):
        self.ip = str(ip)
        self.port = int(port)

        self.locks = locks

        socket.AF_

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self.ip, self.port))

    def __enter__(self):
        return self

    def __close__(self):
        pass

    def listen_connections(self, connections:int=1, ip:str=None, port:int=None):
        if(ip is None): ip = self.ip
        if(port is None): port = self.port
        else: self.port = int(port)
            
        if(self.threaded):
            process = [] #miau
            for _ in range(connections):
                process.append(Process(target=self.new_connection, args=(ip, port)))
                
                process[-1].start()
                
            for conn in process: conn.join()
        else: self.new_connection(ip, port)
    
    def new_connection(self, ip:str=None, port:int=None):
        if(self.max_connections + 1 and len(self._client_from_addr) >= self.max_connections): return
    
        if(ip is None): ip = self.ip
        if(port is None): port = self.port

        self._socket.listen()
            
        listener, addr = self._socket.accept()
        
        logging.info(f"Connected new user: {addr}")
        
        self._client_from_addr[addr] = listener
        self.open[addr] = True

        lock = self.__manager.Lock()
        lock.acquire()

        if(self.threaded):
            self._process_from_addr[addr] = Process(target=self.listen, args=(addr, listener, lock), daemon=True)
            self._process_from_addr[addr].start()
        else: self.listen(addr,listener)
    
        tmp_fname(addr, lock)

    def tmp_fname(self, addr:tuple, lock:Lock):
        lock.release()
        while(self.open[addr]): pass

    def sendto(self, message:str, addr:tuple):
        self._client_from_addr[addr].sendto(bytes(str(message), "utf-8"), addr)

    def sendall(self, message:str):
        self._socket.sendall(bytes(str(message), "utf-8"))
    
    def listen(self, addr, listener, lock:Lock):
        logging.debug("Client.listen(self)")
        if(not self.open[addr]): return
        
        with listener:
            timeout = 0
            while(self.open[addr]):
                lock.acquire()
                data = listener.recv(1024)
                decoded_data = data.decode("utf-8")

                if(data is None):
                    timeout += 1
                    logging.debug(f"Timeout of user {addr} increased to {timeout}")
                    if(timeout > 9): 
                        logging.warning(f"User {addr} has disconnected")
                        break
                elif(decoded_data != ''):
                    timeout = 0
                    logging.info(f"Recived data '{decoded_data}' from address {addr}")
                    
                    lock.release()
                    yield decoded_data

        del self._process_from_addr[addr]
        del self._client_from_addr[addr]
        del self.open[addr]
                                            
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

    def ping(self, addr:tuple, send_time:str=None) -> None:
        if(send_time is None):
            self.client.sendto("--_ping",addr)
            self.listen(addr)

if __name__ == "__main__":
    main()