#!/usr/bin/python
import os
import yaml
import subprocess

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def find_latest_file(dir_path):
    # Get list of all files in dir_path and subdirectories
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dir_path) for f in filenames]
    # Find the latest file
    latest_file = max(files, key=os.path.getctime)
    return latest_file

if __name__ == "__main__":
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    latest_file = find_latest_file(config['image_output'])
    print(f"Applying overlay to {latest_file}")
    subprocess.run(['python', '/home/pi/raspberrypi-picamera-timelapse/overlay.py', latest_file])

