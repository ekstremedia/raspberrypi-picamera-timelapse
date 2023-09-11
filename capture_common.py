#!/usr/bin/python
import datetime
import yaml
import json
import os
import libcamera
from prettytable import PrettyTable
from termcolor import colored

DAYTIME_SHUTTER = 4489
DAYTIME_GAIN = 0
MAX_SHUTTER = 12000000
MAX_GAIN = 8


def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)


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


def load_sun_data():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    sun_data_file = os.path.join(script_dir, 'data', 'sun_data_2023.json')
    with open(sun_data_file, 'r') as file:
        return json.load(file)


def get_sun_times(date, sun_data):
    date_str = date.strftime('%m-%d')
    return sun_data.get(date_str, {}).get('sunrise'), sun_data.get(date_str, {}).get('sunset')


def print_camera_config(camera_config, shutter_speed, gain):
    table = PrettyTable()
    table.field_names = ["Setting", "Value"]
    table.add_row(["Shutter Speed", shutter_speed])
    table.add_row(["Gain", gain])
    for key, value in camera_config['controls'].items():
        table.add_row([key, value])

    print(colored(table, 'green'))
