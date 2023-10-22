#!/usr/bin/python
import os
import subprocess
import datetime
import yaml
import argparse
from colored import fg, attr
from scripts import ffmpeg as ff_script
from scripts.logger import log_message

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def create_timelapse(config, date=None, upload=True, debug=False, only_upload=False):
    # Get the specified or previous day's date
    if date:
        try:
            specified_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            log_message("Invalid date format. Please provide the date in the format 'YYYY-MM-DD'.")
            return
    else:
        specified_date = datetime.date.today() - datetime.timedelta(days=1)

    # Convert date to string format
    specified_date_str = specified_date.strftime('%Y/%m/%d')

    # Generate the video filename and video parameters
    if debug:
        video_filename = f"{specified_date.strftime('%Y_%m_%d')}_{config['video_output']['video_width']}_{config['video_output']['video_height']}_{config['video_output']['constant_rate_factor']}.{config['video_output']['video_format']}"
    else:
        video_filename = f"{config['video_output']['filename_prefix']}{specified_date.strftime('%Y_%m_%d')}.{config['video_output']['video_format']}"

    # Define the video path
    if debug:
        video_folder = "/var/www/html/public/video-debug/"
    else:
        video_folder = os.path.join(config['video_output']['root_folder'], specified_date.strftime(config['video_output']['folder_structure']))

    video_path = os.path.join(video_folder, video_filename)

    # Get the image folder path for the specified date
    image_folder = os.path.join(config['image_output']['root_folder'], specified_date.strftime(config['image_output']['folder_structure']))

    # Check if the image folder exists
    if not os.path.exists(image_folder):
        log_message(f"No images found for {specified_date_str}")
        return

    # Create the timelapse video folder if it doesn't exist
    os.makedirs(video_folder, exist_ok=True)

    if not only_upload:
        ff_script.ffmpeg_command(image_folder, video_path, config)

    # Upload file
    if upload and config.get('video_upload', {}).get('enabled', False):
        upload_script = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts', 'upload-timelapse-video.py')
        date_arg = specified_date.strftime('%Y-%m-%d')  # Format the date as 'YYYY-MM-DD'
        upload_command = ['python', upload_script, '--file', video_path, '--date', date_arg]
        subprocess.run(upload_command, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a timelapse video.')
    parser.add_argument('--date', type=str, required=False, help='The date for which to create a timelapse video. Format: YYYY-MM-DD')
    parser.add_argument('--dont-upload', action='store_true', help='If set, the video will not be uploaded.')
    parser.add_argument('--only-upload', action='store_true', help='If set, only the upload will be done without creating a new timelapse.')
    parser.add_argument('--debug', action='store_true', help='If set, debug mode will be enabled.')
    args = parser.parse_args()

    if args.only_upload and args.dont_upload:
        print("Error: --only-upload and --dont-upload cannot be used together.")
        exit(1)

    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    create_timelapse(config, args.date, not args.dont_upload, args.debug, args.only_upload)