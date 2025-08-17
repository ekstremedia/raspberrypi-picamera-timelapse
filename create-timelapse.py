#!/usr/bin/python
import os
import subprocess
import datetime
import yaml
import argparse
import re
from colored import fg, attr
from scripts import ffmpeg as ff_script
from scripts.logger import log_message

FILENAME_TS_RE = re.compile(r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_(\d{2})')

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def parse_dt_from_filename(name):
    m = FILENAME_TS_RE.search(name)
    if not m:
        return None
    y, mo, d, H, M, S = map(int, m.groups())
    return datetime.datetime(y, mo, d, H, M, S)


def collect_images_in_window(folder, start_dt, end_dt, min_size_kb=30, prefix=None):
    if not os.path.isdir(folder):
        return []
    min_bytes = min_size_kb * 1024
    out = []
    for name in os.listdir(folder):
        if not name.lower().endswith('.jpg'):
            continue
        if prefix and not name.startswith(prefix):
            continue
        p = os.path.join(folder, name)
        try:
            if os.path.getsize(p) < min_bytes:
                continue
        except FileNotFoundError:
            continue
        dt = parse_dt_from_filename(name)
        if not dt:
            continue
        if start_dt <= dt <= end_dt:
            out.append((dt, p))
    out.sort(key=lambda t: t[0])
    return [p for _, p in out]

def get_image_range_for_period(config, specified_date):
    # 05:00 of the given day -> 05:00 next day
    start_dt = datetime.datetime.combine(specified_date, datetime.time(5, 0, 0))
    end_dt = start_dt + datetime.timedelta(days=1)

    day_folder = os.path.join(
        config['image_output']['root_folder'],
        specified_date.strftime(config['image_output']['folder_structure'])
    )
    next_day = specified_date + datetime.timedelta(days=1)
    next_day_folder = os.path.join(
        config['image_output']['root_folder'],
        next_day.strftime(config['image_output']['folder_structure'])
    )

    prefix = config['image_output'].get('filename_prefix') or ''
    selected = []
    selected += collect_images_in_window(day_folder, start_dt, end_dt, prefix=prefix)
    selected += collect_images_in_window(next_day_folder, start_dt, end_dt, prefix=prefix)
    selected.sort()

    if not selected:
        return None, None, []

    return selected[0], selected[-1], selected

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

    # Ensure output folder exists
    os.makedirs(video_folder, exist_ok=True)

    # Identify the starting and ending images (05:00 → 05:00 window)
    start_image, end_image, selected_images = get_image_range_for_period(config, specified_date)

    if not only_upload:
        if not selected_images:
            log_message(f"No images found in 05:00→05:00 window for {specified_date_str}")
            return
        # Build the video (ffmpeg_command now takes absolute image paths)
        ok = ff_script.ffmpeg_command(video_path, config, selected_images)
        if not ok:
            log_message("FFmpeg failed. Skipping upload.")
            return

    # Upload file (only if exists and enabled)
    if upload and config.get('video_upload', {}).get('enabled', False):
        if not os.path.exists(video_path):
            log_message(f"Video not found at {video_path}; skipping upload.")
            return
        upload_script = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts', 'upload-timelapse-video.py')
        date_arg = specified_date.strftime('%Y-%m-%d')
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