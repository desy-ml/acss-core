import threading


class TimerThread(threading.Thread):
    def __init__(self, time: float, func):
        """_summary_
        An thread which will call func periodically. 
        :param time: Defines the time period in seconds.
        :type time: float
        :param func: function that will be called after time is passed
        :type func: _type_
        """
        super().__init__()
        self._stop_event = threading.Event()
        self.time = time
        self.func = func

    def stopped(self):
        return self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.wait(self.time):
            self.func()
