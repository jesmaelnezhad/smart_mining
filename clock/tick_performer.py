from threading import Thread, Lock


class TickPerformer:
    def __init__(self):
        self.t = Thread(target=self.run_all, args=(self.should_stop,), daemon=self.is_a_daemon())
        self.stop_flag = False
        self.stop_flag_mutex = Lock()
        self.execution_ended = False
        self.execution_ended_mutex = Lock()

    def should_end_execution(self):
        self.execution_ended_mutex.acquire()
        try:
            return self.execution_ended
        finally:
            self.execution_ended_mutex.release()

    def set_end_of_execution(self):
        # notify other threads to exit
        self.execution_ended_mutex.acquire()
        try:
            self.execution_ended = True
        finally:
            self.execution_ended_mutex.release()

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

    def run_all(self, should_stop):
        self.run(should_stop)
        self.post_run()
        self.set_end_of_execution()

    def run(self, should_stop):
        pass

    def post_run(self):
        pass

    def is_a_daemon(self):
        # Daemon threads run in the background and they are killed automatically when the
        # main thread exits.
        pass


