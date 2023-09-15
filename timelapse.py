#!/usr/bin/python

import time
import yaml
import subprocess
from datetime import datetime, timedelta
import json
import os

def load_config(config_path):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def load_sun_data():
    """Load sunrise and sunset data from a JSON file."""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    sun_data_file = os.path.join(current_dir, 'data', 'sun_data_2023.json')
    with open(sun_data_file, 'r') as file:
        return json.load(file)

def get_sun_times(date, sun_data):
    """Retrieve sunrise and sunset times for a given date."""
    date_str = date.strftime('%m-%d')
    return sun_data.get(date_str, {}).get('sunrise'), sun_data.get(date_str, {}).get('sunset')

def is_within_transition_period(sunrise_time, sunset_time, config):
    """Check if current time is within the transition period of sunrise or sunset."""
    sunrise = datetime.strptime(sunrise_time, '%H:%M')
    sunset = datetime.strptime(sunset_time, '%H:%M')
    now = datetime.now()
    return sunset <= now <= sunset + timedelta(minutes=config['camera_constants']['POST_SUNSET_DELAY_MINUTES']) or sunrise <= now <= sunrise + timedelta(minutes=config['camera_constants']['SUNRISE_OFFSET_MINUTES'])

def is_nighttime(sunrise_time, sunset_time, config):
    """Determine if the current time is considered nighttime."""
    sunset_end_transition = datetime.strptime(sunset_time, '%H:%M') + timedelta(minutes=config['camera_constants']['POST_SUNSET_DELAY_MINUTES'])
    sunrise_end_transition = datetime.strptime(sunrise_time, '%H:%M') + timedelta(minutes=config['camera_constants']['SUNRISE_OFFSET_MINUTES'])
    now = datetime.now().time()

    # Check post-sunset and pre-sunrise-end-transition conditions
    return sunset_end_transition.time() <= now or now <= sunrise_end_transition.time()

def timelapse(config):
    """Main function to run the timelapse, deciding which capture script to run based on current time and sun data."""
    sun_data = load_sun_data()
    interval = config['interval']
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    while True:
        today = datetime.now().date()
        sunrise_time, sunset_time = get_sun_times(today, sun_data)
        
        if sunrise_time == "never_sets" or sunset_time == "never_sets":
            # Places where the sun doesn't set or rise
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image.py')])
        elif is_within_transition_period(sunrise_time, sunset_time, config):
            # Transition periods (around sunrise and sunset)
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image_night.py')])
        elif is_nighttime(sunrise_time, sunset_time, config):
            # Nighttime
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image_night.py')])
        else:
            # Daytime
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image.py')])

        time.sleep(interval)

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    config = load_config(config_path)
    timelapse(config)
