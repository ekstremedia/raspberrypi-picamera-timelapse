#!/usr/bin/python
import time
import yaml
import subprocess

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def timelapse(config):
    interval = config['interval']
    while True:
        subprocess.run(['python', '/home/pi/raspberrypi-picamera-timelapse/pc.py'])
        time.sleep(interval)

if __name__ == "__main__":
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    timelapse(config)
