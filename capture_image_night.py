import datetime
from dateutil import parser
import yaml
import json
import os
import time
from picamera2 import Picamera2
import shutil
import libcamera
import logging
from overlay import add_overlay
from prettytable import PrettyTable
from termcolor import colored
import argparse

# Constants
DAYTIME_SHUTTER = 4489
DAYTIME_GAIN = 0
MAX_SHUTTER = 12000000
MAX_GAIN = 8
SUNRISE_OFFSET_MINUTES = -60  # Start transition 1 hour before actual sunrise

def parse_arguments():
    parser = argparse.ArgumentParser(description="Capture image script with test mode.")
    parser.add_argument("--test", help="Enable test mode.", action="store_true")
    return parser.parse_args()

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def setup_logging(config):
    if config.get('log_capture_image'):
        log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'capture-image.log')
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        return True
    else:
        return False

def load_camera_state():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    camera_state_file = os.path.join(script_dir, 'data', 'camera_state.json')
    
    try:
        with open(camera_state_file, "r") as file:
            state = json.load(file)
            return state["shutter_speed"], state["gain"], state.get("photo_counter", 0)
    except (FileNotFoundError, KeyError):
        return DAYTIME_SHUTTER, DAYTIME_GAIN, 0

def save_camera_state(shutter_speed, gain, photo_counter):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    camera_state_file = os.path.join(script_dir, 'data', 'camera_state.json')
    with open(camera_state_file, "w") as file:
        json.dump({"shutter_speed": shutter_speed, "gain": gain, "photo_counter": photo_counter}, file)

def load_sun_data(sun_data_file):
    with open(sun_data_file, 'r') as file:
        return json.load(file)

def get_sun_times(date, sun_data):
    date_str = date.strftime('%m-%d')
    return sun_data.get(date_str, {}).get('sunrise'), sun_data.get(date_str, {}).get('sunset')

def is_start_of_night(sunset_time):
    sunset = parser.parse(sunset_time).time()
    now = datetime.datetime.now().time()
    return sunset < now and (datetime.datetime.combine(datetime.date.today(), now) - datetime.datetime.combine(datetime.date.today(), sunset)).seconds <= 300

def compute_increments(shutter_speed, gain):
    duration_in_minutes = 60  # Always 60 minutes for the transition
    if shutter_speed > DAYTIME_SHUTTER:
        shutter_increment = round((shutter_speed - DAYTIME_SHUTTER) / (duration_in_minutes / (50/60)))  # Decrement value, rounded to whole number
    else:
        shutter_increment = round((MAX_SHUTTER - DAYTIME_SHUTTER) / (duration_in_minutes / (50/60)))  # Increment value, rounded to whole number
    return shutter_increment

def print_camera_config(camera_config, shutter_speed, gain):
    table = PrettyTable()
    table.field_names = ["Setting", "Value"]
    table.add_row(["Shutter Speed", shutter_speed])
    table.add_row(["Gain", gain])
    for key, value in camera_config['controls'].items():
        table.add_row([key, value])

    print(colored(table, 'green'))

def capture_night_image(config, logging_enabled, shutter_speed, gain, test_mode=False):
    # Adjust camera settings for night time capturing
    with Picamera2() as camera:
        # Set focus mode and lens position based on config
        focus_mode = libcamera.controls.AfModeEnum.Manual if config['focus_mode'] == 'manual' else libcamera.controls.AfModeEnum.Auto
        lens_position = config['lens_position'] if config['focus_mode'] == 'manual' else None

        camera_config = camera.create_still_configuration(
            main={"size": tuple(config['main_size'])},
            lores={"size": tuple(config['lores_size'])},
            display=config['display'],
            controls={
                "AwbEnable": config['awb_enable'],
                "AwbMode": getattr(libcamera.controls.AwbModeEnum, config['awb_mode']),
                "AfMode": focus_mode,
                "LensPosition": lens_position,
                "ColourGains": tuple(config['colour_gains']),
                "ExposureTime": int(shutter_speed),
                "AnalogueGain": gain
            }
        )
        
        if test_mode:
            print_camera_config(camera_config, shutter_speed, gain)
            
        camera.options['quality'] = config['image_quality']
        camera.configure(camera_config)

        if logging_enabled:
            logging.info(f"Camera config: {camera_config}")

        camera.start()
        time.sleep(5)  # Allow the camera to adjust

        if test_mode:
            file_name = os.path.join(config['image_output']['test_folder'], 'test.jpg')
        else:
            now = datetime.datetime.now()
            dir_name = os.path.join(config['image_output']['root_folder'], now.strftime(config['image_output']['folder_structure']))
            os.makedirs(dir_name, exist_ok=True)
            file_name = os.path.join(dir_name, f"{config['image_output']['filename_prefix']}{now.strftime('%Y_%m_%d_%H_%M_%S')}.jpg")

        camera.capture_file(file_name)

        if not test_mode and config['overlay']['enabled']:
            add_overlay(config, file_name)

        if logging_enabled:
            logging.info(f"Image captured and saved to {file_name}")

        if config['status_file'] and not test_mode:
            shutil.copy2(file_name, config['status_file'])

        print(f"Saved file {file_name}")

def is_one_hour_before_sunrise(sunrise_time):
    sunrise_with_offset = parser.parse(sunrise_time) + datetime.timedelta(minutes=SUNRISE_OFFSET_MINUTES)
    now = datetime.datetime.now()
    delta = sunrise_with_offset - now
    return 0 < delta.total_seconds() <= 3600  # Check if now is within one hour before adjusted sunrise


if __name__ == "__main__":
    args = parse_arguments()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    config = load_config(os.path.join(script_dir, 'config.yaml'))
    sun_data_file = os.path.join(script_dir, 'data', 'sun_data_2023.json')
    sun_data = load_sun_data(sun_data_file)

    # Load sunset and sunrise times
    today = datetime.datetime.now().date()
    sunrise_time, sunset_time = get_sun_times(today, sun_data)

    if sunrise_time == "never_sets" or sunset_time == "never_sets":
        exit()

    if is_start_of_night(sunset_time):
        shutter_speed = DAYTIME_SHUTTER
        gain = DAYTIME_GAIN
        photo_counter = 0
    else:
        shutter_speed, gain, photo_counter = load_camera_state()

    duration_in_minutes = (parser.parse(sunrise_time) - datetime.datetime.now()).seconds // 60
    shutter_increment = compute_increments(shutter_speed, gain)

    if is_one_hour_before_sunrise(sunrise_time):
        shutter_speed -= shutter_increment
        if shutter_speed < DAYTIME_SHUTTER:
            shutter_speed = DAYTIME_SHUTTER

        photo_counter += 1
        if photo_counter % 9 == 0 and gain > 0:
            gain -= 1
    else:
        shutter_speed += shutter_increment
        if shutter_speed > MAX_SHUTTER:
            shutter_speed = MAX_SHUTTER

        photo_counter += 1
        if photo_counter % 9 == 0 and gain < 8:
            gain += 1

    gain = int(gain)  # Convert to integer
    shutter_speed = int(shutter_speed)  # Convert to integer

    logging_enabled = setup_logging(config)
    capture_night_image(config, logging_enabled, shutter_speed, gain, test_mode=args.test)

    save_camera_state(shutter_speed, gain, photo_counter)