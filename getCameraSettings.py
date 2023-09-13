from picamera2 import Picamera2
import libcamera
from prettytable import PrettyTable
from termcolor import colored

# Define the constants for each attribute. Default is True.
SHOW_CAMERA_CONFIG = True
SHOW_CAMERA_CONTROLS = True
SHOW_CAMERA_CTRL_INFO = True

def wrap_in_color(text, color):
    RESET_COLOR = "\033[0m"
    colored_text = colored(text, color)
    return colored_text + RESET_COLOR

def print_camera_ctrl_info(title, ctrl_info_dict):
    """
    Create and print a PrettyTable for the camera_ctrl_info dictionary.
    """
    table = PrettyTable()
    table.field_names = ["Control", "Control ID", "Control Type", "Control Info"]

    for control, info in ctrl_info_dict.items():
        ctrl_id = info[0]
        ctrl_info = info[1]
        
        ctrl_id_str = f"{ctrl_id.name} ({ctrl_id.id})"
        ctrl_type_str = ctrl_id.type
        ctrl_info_str = f"Min: {ctrl_info.min}\nMax: {ctrl_info.max}\nDefault: {ctrl_info.default}"

        colored_control = wrap_in_color(control, 'blue')
        colored_ctrl_id = wrap_in_color(ctrl_id_str, 'green')
        colored_ctrl_type = wrap_in_color(ctrl_type_str, 'green')
        colored_ctrl_info = wrap_in_color(ctrl_info_str, 'green')
        
        table.add_row([colored_control, colored_ctrl_id, colored_ctrl_type, colored_ctrl_info])

    header = f"{wrap_in_color('Control', 'blue'):<20} | {wrap_in_color('Control ID', 'green'):<20} | {wrap_in_color('Control Type', 'green'):<20} | {wrap_in_color('Control Info', 'green')}"
    print(colored(title, 'yellow'))
    print(header)
    print(table.get_string(header=False))

def print_table(title, dictionary):
    """
    Create and print a PrettyTable for the given dictionary.
    """
    table = PrettyTable()
    table.field_names = ["Key", "Value"]
    
    for key, value in dictionary.items():
        if isinstance(value, dict):
            value_str = "\n".join([f"{k}: {v}" for k, v in value.items()])
        else:
            value_str = str(value)
        
        colored_key = wrap_in_color(key, 'blue')
        colored_value = wrap_in_color(value_str, 'green')
        
        table.add_row([colored_key, colored_value])

    header = f"{wrap_in_color('Key', 'blue'):<20} | {wrap_in_color('Value', 'green')}"
    print(colored(title, 'yellow'))
    print(header)
    print(table.get_string(header=False))

with Picamera2() as camera:
    attributes = [attr for attr in dir(camera) if not callable(getattr(camera, attr)) and not attr.startswith("__")]
    for attribute in attributes:
        value = getattr(camera, attribute)
        
        if attribute == 'camera_ctrl_info':
            print_camera_ctrl_info(attribute, value)
        elif isinstance(value, dict):
            if 'SHOW_' + attribute.upper() in globals() and globals()['SHOW_' + attribute.upper()]:
                print_table(attribute, value)

#with Picamera2() as camera:
#   attributes = [attr for attr in dir(camera) if not callable(getattr(camera, attr)) and not attr.startswith("__")]
#   for attribute in attributes:
#       print(attribute, ":", getattr(camera, attribute))

with Picamera2() as camera:
    current_exposure_time = camera.controls['ExposureTime'] if 'ExposureTime' in camera.controls else None
    if current_exposure_time is not None:
        print(f"Current ExposureTime: {current_exposure_time}")
    else:
        print("Couldn't find the current ExposureTime.")
