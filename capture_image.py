#!/usr/bin/python
import time
import yaml
import os
from datetime import datetime
from picamera2 import Picamera2
import shutil
import libcamera
import subprocess
import logging
from overlay import add_overlay  # import add_overlay function from overlay.py
import json 

# Load configuration from yaml file
def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)


DAYTIME_SHUTTER = 4489
DAYTIME_GAIN = 1

def reset_to_daytime_settings():
    """Reset the camera settings to daytime values if they are not already."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    camera_state_file = os.path.join(script_dir, 'data', 'camera_state.json')

    # Load existing state
    try:
        with open(camera_state_file, "r") as file:
            state = json.load(file)
    except FileNotFoundError:
        state = {}

    # Update only shutter_speed and gain to daytime values
    state["shutter_speed"] = DAYTIME_SHUTTER
    state["gain"] = DAYTIME_GAIN

    # Save the updated state
    with open(camera_state_file, "w") as file:
        json.dump(state, file)

# Set up logging
def setup_logging(config):
    if config.get('log_capture_image'):
        log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'capture-image.log')
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        return True
    else:
        return False

def capture_image(config, logging_enabled):
    # Enable or disable HDR based on config
    # This must be done before Picamera2 is ran
    # Only works with v3 cameras
    if config['hdr']:
        os.system("v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0")
    else:
        os.system("v4l2-ctl --set-ctrl wide_dynamic_range=0 -d /dev/v4l-subdev0")

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
                "AnalogueGain": 1
            }
        )
        camera.options['quality'] = config['image_quality']
        print(f"libcamera.controls {libcamera.controls}")
        
        camera.configure(camera_config)
        # Log out all active controls before capturing the image
        if logging_enabled:
            logging.info(f"Camera config: {camera_config}")

        camera.start()
        time.sleep(2)  # Allow the camera to adjust

        now = datetime.now()
        dir_name = os.path.join(config['image_output']['root_folder'], now.strftime(config['image_output']['folder_structure']))
        os.makedirs(dir_name, exist_ok=True)
        file_name = os.path.join(dir_name, f"{config['image_output']['filename_prefix']}{now.strftime('%Y_%m_%d_%H_%M_%S')}.jpg")
        camera.capture_file(file_name)

        if config['overlay']['enabled']:
            add_overlay(config, file_name)

        if logging_enabled:
            logging.info(f"Image captured and saved to {file_name}")

        if (config['status_file']):
            shutil.copy2(file_name, config['status_file'])            
            print(f"Copied {file_name} to {config['status_file']}")
        
        print(f"Saved file {file_name}")

if __name__ == "__main__":
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    logging_enabled = setup_logging(config)
    reset_to_daytime_settings()
    capture_image(config, logging_enabled)
