from threading import Thread, Lock


class TickPerformer:
    def __init__(self):
        self.t = Thread(target=self.run, args=(self.should_stop,), daemon=self.is_a_daemon())
        self.stop_flag = False
        self.stop_flag_mutex = Lock()

    def stop(self):
        self.stop_flag_mutex.acquire()
        try:
            self.stop_flag = True
        finally:
            self.stop_flag_mutex.release()

    def should_stop(self):
        self.stop_flag_mutex.acquire()
        try:
            return self.stop_flag
        finally:
            self.stop_flag_mutex.release()

    def start(self):
        self.t.start()

    def join(self):
        if not self.is_a_daemon():
            self.t.join()

    def run(self, should_stop):
        pass

    def is_a_daemon(self):
        pass


