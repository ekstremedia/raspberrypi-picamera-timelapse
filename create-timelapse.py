#!/usr/bin/python
import os
import subprocess
import time
import datetime
import yaml
import sys

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def create_timelapse(config, date=None):
    # Get the specified or previous day's date
    if date:
        try:
            specified_date = datetime.datetime.strptime(date, '%Y/%m/%d').date()
        except ValueError:
            print("Invalid date format. Please provide the date in the format 'YYYY/MM/DD'.")
            return
    else:
        specified_date = datetime.date.today() - datetime.timedelta(days=1)

    # Convert date to string format
    specified_date_str = specified_date.strftime('%Y/%m/%d')

    # Get the image folder path for the specified date
    image_folder = os.path.join(config['image_output'], specified_date_str)

    # Check if the image folder exists
    if not os.path.exists(image_folder):
        print(f"No images found for {specified_date_str}")
        return

    # Create the timelapse video folder if it doesn't exist
    video_folder = os.path.join(config['timelapse_video_folder'], specified_date.strftime('%Y/%m'))
    os.makedirs(video_folder, exist_ok=True)

    # Generate the video filename
    video_filename = f"{config['video_filename_prefix']}{specified_date.strftime('%Y_%m_%d')}.{config['video_format']}"
    video_path = os.path.join(video_folder, video_filename)

    # Build the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-y',  # Overwrite the output file without asking for confirmation
        '-framerate', str(config['framerate']),
        '-pattern_type', 'glob',
        '-i', f"{image_folder}/*.jpg",
        '-c:v', 'libx264',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-b:v', str(config['bitrate']),
        video_path
    ]

    # Run the ffmpeg command
    subprocess.run(ffmpeg_command, capture_output=True, text=True, check=True)

    print(f"Timelapse video created: {video_path}")

if __name__ == "__main__":
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    create_timelapse(config, date_arg)
