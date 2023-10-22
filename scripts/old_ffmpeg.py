#!/usr/bin/python
import subprocess
import os
import time
from colored import fg, attr
from .logger import log_message

def format_duration(duration):
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    return f"{minutes} minutes, {seconds} seconds"

def ffmpeg_command(image_folder, video_path, config):
    ffmpeg_settings = [
        ('-y', None),  # Overwrite the output file without asking for confirmation
        ('-framerate', str(config['video_output']['framerate'])),
        ('-pattern_type', 'glob'),
        ('-i', f"{os.path.join(image_folder, '*.jpg')}"),
        ('-s', f"{config['video_output']['video_width']}x{config['video_output']['video_height']}"),
        ('-vf', f"deflicker,setpts=N/FRAME_RATE/TB"),
        ('-c:v', 'libx264'),
        ('-crf', str(config['video_output']['constant_rate_factor'])),
        ('-b:v', str(config['video_output']['bitrate']))
    ]
    # Build the ffmpeg command
    ffmpeg_command = ['ffmpeg'] + [item for sublist in ffmpeg_settings for item in sublist if item is not None] + [video_path]

    # Display FFmpeg information settings
    log_message(f"{fg('green')}FFmpeg Information Settings{attr('reset')}")
    for setting in ffmpeg_settings:
        if setting[1] is not None:
            log_message(f"{fg('cyan')}{setting[0]} {attr('reset')}{fg(244)}{setting[1]}{attr('reset')}")

    log_message(f"{fg('green')}Starting timelapse...{attr('reset')}")

    start_time = time.time()
    output = subprocess.run(ffmpeg_command, )
    # output = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    end_time = time.time()

    duration = end_time - start_time
    formatted_duration = format_duration(duration)

    log_message(f"{fg('green')}Timelapse video created{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{video_path}{attr('reset')}")
    log_message(f"{fg('green')}Duration{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{formatted_duration}")
