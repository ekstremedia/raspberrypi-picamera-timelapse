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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Capture image script with test mode.")
    parser.add_argument("--test", help="Enable test mode.", action="store_true")
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def load_sun_data(sun_data_file):
    with open(sun_data_file, 'r') as file:
        return json.load(file)


def get_sun_times(date, sun_data):
    """Get sunrise and sunset times for a given date."""
    date_str = date.strftime('%m-%d')
    return sun_data.get(date_str, {}).get('sunrise'), sun_data.get(date_str, {}).get('sunset')

def is_after_sunset(sunset_time):
    """Determine if the current time is after sunset."""
    sunset = parser.parse(sunset_time)
    now = datetime.datetime.now()
    return now > sunset

def is_transition_before_sunrise(sunrise_time):
    """Determine if the current time is within the transition period before sunrise."""
    sunrise = parser.parse(sunrise_time)
    transition_start = sunrise + datetime.timedelta(minutes=SUNRISE_OFFSET_MINUTES)
    now = datetime.datetime.now()
    return transition_start <= now < sunrise

def compute_shutter_increments():
    """Compute the shutter speed increments for the transition period."""
    return (MAX_SHUTTER - DAYTIME_SHUTTER) // 60  # 60 minutes for the transition

def compute_gain_increments():
    """Compute the gain increments for the transition period."""
    return (MAX_GAIN - DAYTIME_GAIN) / 60.0  # 60 minutes for the transition, use floating point division

def print_camera_config(camera_config, shutter_speed, gain):
    """Print the current camera configuration in a table format."""
    table = PrettyTable()
    table.field_names = ["Setting", "Value"]
    table.add_row(["Shutter Speed", shutter_speed])
    table.add_row(["Gain", gain])
    for key, value in camera_config['controls'].items():
        table.add_row([key, value])
    print(colored(table, 'green'))

def setup_logging(config):
    """Setup logging based on the provided configuration."""
    if config.get('log_capture_image'):
        log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'capture-image.log')
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        return True
    else:
        return False

def load_camera_state():
    """Load the camera state (shutter speed, gain) from a JSON file."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    camera_state_file = os.path.join(script_dir, 'data', 'camera_state.json')
    try:
        with open(camera_state_file, "r") as file:
            state = json.load(file)
            return state["shutter_speed"], max(1, state["gain"]), state.get("photo_counter", 0), state.get("gain_increment_counter", 0)
    except (FileNotFoundError, KeyError):
        return DAYTIME_SHUTTER, max(1, DAYTIME_GAIN), 0, 0

def save_camera_state(shutter_speed, gain, photo_counter, gain_increment_counter):
    """Save the camera state (shutter speed, gain) to a JSON file."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    camera_state_file = os.path.join(script_dir, 'data', 'camera_state.json')
    with open(camera_state_file, "w") as file:
        json.dump({"shutter_speed": shutter_speed, "gain": gain, "photo_counter": photo_counter, "gain_increment_counter": gain_increment_counter}, file)

def capture_night_image(config, logging_enabled, shutter_speed, gain, test_mode=False):
    """Capture an image with night settings."""
    with Picamera2() as camera:
        # Set focus mode and lens position based on config
        focus_mode = libcamera.controls.AfModeEnum.Manual if config['focus_mode'] == 'manual' else libcamera.controls.AfModeEnum.Auto
        lens_position = config['lens_position'] if config['focus_mode'] == 'manual' else None

        # Create the camera configuration
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
                "AnalogueGain": round(gain)
            }
        )
        
        print_camera_config(camera_config, shutter_speed, gain)
        camera.options['quality'] = config['image_quality']
        camera.configure(camera_config)

        if logging_enabled:
            logging.info(f"Camera config: {camera_config}")

        camera.start()
        time.sleep(5)  # Allow the camera to adjust

        # Determine the file name for the captured image
        if test_mode:
            file_name = os.path.join(config['image_output']['test_folder'], 'test.jpg')
        else:
            now = datetime.datetime.now()
            dir_name = os.path.join(config['image_output']['root_folder'], now.strftime(config['image_output']['folder_structure']))
            os.makedirs(dir_name, exist_ok=True)
            file_name = os.path.join(dir_name, f"{config['image_output']['filename_prefix']}{now.strftime('%Y_%m_%d_%H_%M_%S')}.jpg")

        # Capture the image and save it
        camera.capture_file(file_name)

        if not test_mode and config['overlay']['enabled']:
            add_overlay(config, file_name)

        if logging_enabled:
            logging.info(f"Image captured and saved to {file_name}")

        if config['status_file'] and not test_mode:
            shutil.copy2(file_name, config['status_file'])

        print(f"Saved file {file_name}")

if __name__ == "__main__":
    args = parse_arguments()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config = load_config(os.path.join(script_dir, 'config.yaml'))

    # Load constants from config
    DAYTIME_SHUTTER = config['camera_constants']['DAYTIME_SHUTTER']
    DAYTIME_GAIN = config['camera_constants']['DAYTIME_GAIN']
    MAX_SHUTTER = config['camera_constants']['MAX_SHUTTER']
    MAX_GAIN = config['camera_constants']['MAX_GAIN']
    SUNRISE_OFFSET_MINUTES = config['camera_constants']['SUNRISE_OFFSET_MINUTES']

    sun_data_file = os.path.join(script_dir, 'data', 'sun_data_2023.json')
    sun_data = load_sun_data(sun_data_file)
    today = datetime.datetime.now().date()
    sunrise_time, sunset_time = get_sun_times(today, sun_data)

    if sunrise_time == "never_sets" or sunset_time == "never_sets":
        exit()

    shutter_speed, gain, photo_counter, gain_increment_counter = load_camera_state()

    # Adjust shutter speed and gain based on current time relative to sunset/sunrise
    if is_after_sunset(sunset_time):
        print(f"Within transition period after sunset. Current shutter_speed: {shutter_speed}, gain: {gain}")
        shutter_speed += compute_shutter_increments()
        gain_increment = compute_gain_increments()
        gain_increment_counter += gain_increment
        if gain_increment_counter >= 1:
            gain += int(gain_increment_counter)
            gain_increment_counter -= int(gain_increment_counter)
        if shutter_speed > MAX_SHUTTER:
            shutter_speed = MAX_SHUTTER
        if gain > MAX_GAIN:
            gain = MAX_GAIN

    elif is_transition_before_sunrise(sunrise_time):
        print(f"Within transition period before sunrise. Current shutter_speed: {shutter_speed}, gain: {gain}")
        shutter_speed -= compute_shutter_increments()
        gain_increment = compute_gain_increments()
        gain_increment_counter -= gain_increment
        if gain_increment_counter <= -1:
            gain += int(gain_increment_counter)
            gain_increment_counter -= int(gain_increment_counter)
        if shutter_speed < DAYTIME_SHUTTER:
            shutter_speed = DAYTIME_SHUTTER
        if gain < 1:
            gain = 1
                
    print(f"After adjustment. New shutter_speed: {shutter_speed}, gain: {gain}")

    gain = int(gain)
    shutter_speed = int(shutter_speed)
    logging_enabled = setup_logging(config)
    capture_night_image(config, logging_enabled, shutter_speed, gain, test_mode=args.test)
    save_camera_state(shutter_speed, gain, photo_counter, gain_increment_counter)
