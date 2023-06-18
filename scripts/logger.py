#!/usr/bin/python
import os
import time
from colored import fg, attr

def log_message(*messages):
    script_path = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(script_path, '..', 'logs', 'timelapse.log')
    log_dir = os.path.dirname(log_path)
    os.makedirs(log_dir, exist_ok=True)

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {attr('reset')}{' '.join(map(str, messages))}\n"

    print(*messages)  # Print the messages with colors

    with open(log_path, 'a') as log_file:
        log_file.write(log_line)
