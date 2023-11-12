import sys
import os
import datetime


class PrintStream:
    def __init__(self, streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            if data == '\n':
                stream.write(data)
            else:
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("[%Y-%m-%d %H:%M:%S] ")
                stream.write(formatted_time + data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


class LogUtil:
    @staticmethod
    def enable():
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(current_file_path, 'logs')
        os.makedirs(log_path, exist_ok=True)

        current_date = datetime.datetime.now()
        log_file_name = current_date.strftime("main_%Y%m%d_%H%M.log")
        log_file_path = os.path.join(log_path, log_file_name)
        log_stream = open(log_file_path, 'a')
        sys.stdout = PrintStream([sys.stdout, log_stream])
        sys.stderr = PrintStream([sys.stderr, log_stream])
