#!/usr/bin/python
import os
import subprocess
import time
import datetime
import yaml
import sys
from colored import fg, attr

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def create_timelapse(config, date=None, debug_mode=False):
    # Get the specified or previous day's date
    if date:
        try:
            specified_date = datetime.datetime.strptime(date, '%Y/%m/%d').date()
        except ValueError:
            log_message("Invalid date format. Please provide the date in the format 'YYYY/MM/DD'.")
            return
    else:
        specified_date = datetime.date.today() - datetime.timedelta(days=1)

    # Convert specified_date to a datetime.datetime object
    specified_datetime = datetime.datetime.combine(specified_date, datetime.datetime.min.time())

    # Convert date to string format
    specified_date_str = specified_date.strftime('%Y/%m/%d')

    # Get the image folder path for the specified date
    image_folder = os.path.join(config['image_output']['root_folder'], specified_date.strftime(config['image_output']['folder_structure']))

    # Check if the image folder exists
    if not os.path.exists(image_folder):
        log_message(f"No images found for {specified_date_str}")
        return

    # Create the timelapse video folder if it doesn't exist
    video_folder = os.path.join(config['video_output']['root_folder'], specified_date.strftime(config['video_output']['folder_structure']))
    os.makedirs(video_folder, exist_ok=True)

    # Generate the video filename and video parameters
    if debug_mode:
        video_filename = f"{config['video_output']['filename_prefix']}{specified_date.strftime('%Y_%m_%d')}_debug.{config['video_format']}"
        video_width = config['debug_mode']['video_width']
        video_height = config['debug_mode']['video_height']
        video_quality = config['debug_mode']['video_quality']
    else:
        video_filename = f"{config['video_output']['filename_prefix']}{specified_date.strftime('%Y_%m_%d')}.{config['video_format']}"
        video_width = config['video_output']['video_width']
        video_height = config['video_output']['video_height']
        video_quality = config['video_output']['video_quality']

    video_path = os.path.join(video_folder, video_filename)

    # Get the image files in the specified date range, sorted by creation time (oldest first)
    image_files = sorted(os.listdir(image_folder), key=lambda f: os.path.getmtime(os.path.join(image_folder, f)))

    # Build the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-y',  # Overwrite the output file without asking for confirmation
        '-framerate', str(config['framerate']),
        '-pattern_type', 'glob',
        '-i', f"{os.path.join(image_folder, '*.jpg')}",
        '-vf', f"minterpolate='mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me_range=16',deflicker",
        '-c:v', 'libx264',
        '-crf', str(video_quality),
        '-pix_fmt', 'yuv420p',
        '-vf', f"scale={video_width}:{video_height}",
        '-b:v', str(config['bitrate']),
        video_path
    ]

    log_message(f"{fg('green')}Starting timelapse...{attr('reset')}")

    start_time = time.time()
    output = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    end_time = time.time()

    log_message(f"{fg('green')}Timelapse video created{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{video_path}{attr('reset')}")
    log_message(f"{fg('green')}Duration{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{end_time - start_time:.2f} seconds")

def log_message(*messages):
    log_path = os.path.join('logs', 'timelapse.log')
    log_dir = os.path.dirname(log_path)
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {attr('reset')}{' '.join(map(str, messages))}\n"

    print(*messages)  # Print the messages with colors

    with open(log_path, 'a') as log_file:
        log_file.write(log_line)

if __name__ == "__main__":
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    debug_mode = sys.argv[2] == "debug" if len(sys.argv) > 2 else False

    create_timelapse(config, date_arg, debug_mode)
