#!/usr/bin/env python3.10
import yaml
from colorama import Fore, Style
import logging


# Function to print and log messages
def print_and_log(message, color=Fore.RESET):
    print(color + message + Style.RESET_ALL)
    logging.info(message)


# Load the config file
with open("config.yaml", 'r') as stream:
    try:
        print_and_log("Loading configuration...", Fore.YELLOW)
        config = yaml.safe_load(stream)
        print_and_log("Configuration loaded successfully.", Fore.GREEN)
    except yaml.YAMLError as exc:
        print_and_log(f"Error in configuration file: {exc}", Fore.RED)
        exit(1)

# Import the appropriate camera module based on the mock_camera config value
if config['camera']['mock_camera']:
    from mock_camera import MockCamera as Camera
else:
    from camera import Camera

# Setup logging
logging.basicConfig(filename='timelapse.log', level=logging.INFO)

if __name__ == "__main__":
    # Initialize and start recording
    camera = Camera(tuple(config['camera']['resolution']), config['camera']['framerate'])
    print_and_log("Starting recording...", Fore.YELLOW)
    camera.record(10)
    print_and_log("Recording completed.", Fore.GREEN)
