import time

class Waiter:
    #last_waited = time.perf_counter() - 10
    def __init__(self, wait_time):
        self.wait_time = wait_time
        self.last_waited = time.perf_counter() - 10
    def wait(self, debug=False):
        time_since = time.perf_counter() - self.last_waited

        if time_since < self.wait_time:
            if debug: print(f"waiting for {round(self.wait_time - time_since, 3)}s")
            time.sleep(self.wait_time - time_since)
        elif debug: print(f"waiting for 0s")
        
        self.last_waited = time.perf_counter()
            

waiter = Waiter(10)