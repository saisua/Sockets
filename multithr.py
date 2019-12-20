import threading

class Process(threading.Thread):
    def __init__(self, target, args:tuple=(), *, daemon:bool=False):
        threading.Thread.__init__(self, daemon=daemon)

        self.target = target

        self.args = args

        self._tmp_result = None 

    def run(self):
        self._tmp_result = self.target(*self.args)

    def __enter__(self, target=None, args:tuple=None):
        if(not target is None): self.target = target
        elif(self.target is None): raise ValueError("Process.target")

        if(not args is None): self.args = args

        self.start()

        return self

    def __close__(self):
        self.join()