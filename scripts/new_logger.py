#!/usr/bin/python
import os
import time

class Logger:
    def __init__(self, log_file_name='general.log'):
        self.log_file_name = log_file_name
        self.script_path = os.path.dirname(os.path.realpath(__file__))

    def log_message(self, *messages):
        log_path = os.path.join(self.script_path, '..', 'logs', self.log_file_name)
        log_dir = os.path.dirname(log_path)
        os.makedirs(log_dir, exist_ok=True)

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {' '.join(map(str, messages))}\n"

        print(*messages)  # Print the messages with colors

        with open(log_path, 'a') as log_file:
            log_file.write(log_line)

# Example usage:
# logger = Logger('custom.log')
# logger.log_message("This is a test message")
