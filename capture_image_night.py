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
from overlay import add_overlay  # If you're using this from the daytime script

# Constants
DAYTIME_SHUTTER = 4489
DAYTIME_GAIN = 0
MAX_SHUTTER = 12000000
MAX_GAIN = 8

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
            return state["shutter_speed"], state["gain"]
    except (FileNotFoundError, KeyError):
        return DAYTIME_SHUTTER, DAYTIME_GAIN


def save_camera_state(shutter_speed, gain):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    camera_state_file = os.path.join(script_dir, 'data', 'camera_state.json')
    with open(camera_state_file, "w") as file:
        json.dump({"shutter_speed": shutter_speed, "gain": gain}, file)


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

def compute_increments(duration_in_minutes):
    shutter_increment = (MAX_SHUTTER - DAYTIME_SHUTTER) / duration_in_minutes
    gain_increment = (MAX_GAIN - DAYTIME_GAIN) / duration_in_minutes
    return shutter_increment, gain_increment

def capture_night_image(config, logging_enabled, shutter_speed, gain):
    # Adjust camera settings for night time capturing
    with Picamera2() as camera:
        # Set focus mode and lens position based on config
        focus_mode = libcamera.controls.AfModeEnum.Manual if config['focus_mode'] == 'manual' else libcamera.controls.AfModeEnum.Auto
        lens_position = config['lens_position'] if config['focus_mode'] == 'manual' else None

        # Debugging lines
        # print(f"Shutter Speed: {shutter_speed}, Type: {type(shutter_speed)}")
        # print(f"Gain: {gain}, Type: {type(gain)}")

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
                "AnalogueGain": (gain)
            }
        )

        camera.options['quality'] = config['image_quality']
        camera.configure(camera_config)
        if logging_enabled:
            logging.info(f"Camera config: {camera_config}")

        camera.start()
        time.sleep(5)  # Allow the camera to adjust

        now = datetime.datetime.now()
        dir_name = os.path.join(config['image_output']['root_folder'], now.strftime(config['image_output']['folder_structure']))
        os.makedirs(dir_name, exist_ok=True)
        file_name = os.path.join(dir_name, f"{config['image_output']['filename_prefix']}{now.strftime('%Y_%m_%d_%H_%M_%S')}.jpg")

        camera.capture_file(file_name)

        if config['overlay']['enabled']:
            add_overlay(config, file_name)

        if logging_enabled:
            logging.info(f"Image captured and saved to {file_name}")

        if config['status_file']:
            shutil.copy2(file_name, config['status_file'])

# Main function
if __name__ == "__main__":
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
        shutter_speed = int(DAYTIME_SHUTTER)
        gain = int(DAYTIME_GAIN)
    else:
        shutter_speed, gain = load_camera_state()

    duration_in_minutes = (parser.parse(sunrise_time) - datetime.datetime.now()).seconds // 60
    shutter_increment, gain_increment = compute_increments(duration_in_minutes)

    logging_enabled = setup_logging(config)
    capture_night_image(config, logging_enabled, shutter_speed, gain)
    
    # Update and save the camera state
    if shutter_speed < MAX_SHUTTER:
        shutter_speed = int(shutter_speed + shutter_increment)
    if gain < MAX_GAIN:
        gain = int(gain + gain_increment)

    save_camera_state(shutter_speed, gain)
