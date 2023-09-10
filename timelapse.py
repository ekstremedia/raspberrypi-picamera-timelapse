#!/usr/bin/python
import time
import yaml
import subprocess
from datetime import datetime, timedelta
import json
import os

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def load_sun_data():
    with open('./data/sun_data_2023.json', 'r') as file:
        return json.load(file)

def get_sun_times(date, sun_data):
    date_str = date.strftime('%m-%d')
    return sun_data.get(date_str, {}).get('sunrise'), sun_data.get(date_str, {}).get('sunset')

def is_nighttime(sunrise_time, sunset_time, offset_hours=3):
    now = datetime.now().time()
    sunrise = datetime.strptime(sunrise_time, '%H:%M').time()
    adjusted_sunset = (datetime.strptime(sunset_time, '%H:%M') + timedelta(hours=offset_hours)).time()
    return adjusted_sunset < now or now < sunrise

def timelapse(config):
    sun_data = load_sun_data()
    interval = config['interval']
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    while True:
        today = datetime.now().date()
        sunrise_time, sunset_time = get_sun_times(today, sun_data)
        
        # If there's "never_sets", just run the daytime script
        if sunrise_time == "never_sets" or sunset_time == "never_sets":
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image.py')])
        # If it's nighttime, run the nighttime script
        elif is_nighttime(sunrise_time, sunset_time):
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image_night.py')])
        # Otherwise, run the daytime script
        else:
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image.py')])
        
        time.sleep(interval)

if __name__ == "__main__":
    config = load_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml'))
    timelapse(config)
