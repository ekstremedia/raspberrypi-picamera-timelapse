#!/usr/bin/python
import time
import yaml
import os
from datetime import datetime
from picamera2 import Picamera2
import libcamera
import subprocess

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def capture_image(config):
    with Picamera2() as camera:
        camera_config = camera.create_still_configuration(
            main={"size": tuple(config['main_size'])},
            lores={"size": tuple(config['lores_size'])},
            display=config['display'],
            controls={
                "AwbEnable": config['awb_enable'],
                "AwbMode": getattr(libcamera.controls.AwbModeEnum, config['awb_mode'])
            }
        )
        camera.configure(camera_config)
        camera.set_controls({"ColourGains": tuple(config['colour_gains'])})

        camera.start()
        time.sleep(2)  # Allow the white balance to adjust

        now = datetime.now()
        dir_name = os.path.join(config['image_output']['root_folder'], now.strftime(config['image_output']['folder_structure']))
        os.makedirs(dir_name, exist_ok=True)
        file_name = os.path.join(dir_name, f"{config['image_output']['filename_prefix']}{now.strftime('%Y_%m_%d_%H_%M_%S')}.jpg")

        camera.capture_file(file_name)
        subprocess.run(['python', '/home/pi/raspberrypi-picamera-timelapse/overlay.py', file_name])
        print("Finished")

if __name__ == "__main__":
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    capture_image(config)
