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

def ffmpeg_command(image_folder, video_path, config, image_files):
    # Generate the list of image files for FFmpeg
    list_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'ffmpeg_list.txt')
    
    with open(list_path, 'w') as f:
        for image_file in image_files:
            # Determine the correct folder for each image based on its filename
            date_part = image_file.split('_')[1:4]
            correct_folder = os.path.join(config['image_output']['root_folder'], *date_part)
            f.write(f"file '{os.path.join(correct_folder, image_file)}'\n")

    ffmpeg_settings = [
        ('-y', None),  # Overwrite the output file without asking for confirmation
        ('-f', 'concat'),
        ('-safe', '0'),
        ('-i', list_path),
        ('-framerate', str(config['video_output']['framerate'])),
        ('-s', f"{config['video_output']['video_width']}x{config['video_output']['video_height']}"),
        ('-vf', f"deflicker,setpts=N/FRAME_RATE/TB"),
        ('-c:v', 'libx264'),
        ('-crf', str(config['video_output']['constant_rate_factor'])),
        ('-b:v', str(config['video_output']['bitrate']))
    ]
    # Build the ffmpeg command
    ffmpeg_command = [
        'ffmpeg'] + [item for sublist in ffmpeg_settings for item in sublist if item is not None] + [video_path]

    # Display FFmpeg information settings
    log_message(f"{fg('green')}FFmpeg Information Settings{attr('reset')}")
    for setting in ffmpeg_settings:
        if setting[1] is not None:
            log_message(
                f"{fg('cyan')}{setting[0]} {attr('reset')}{fg(244)}{setting[1]}{attr('reset')}")

    log_message(f"{fg('green')}Starting timelapse...{attr('reset')}")

    start_time = time.time()
    # output = subprocess.run(ffmpeg_command)
    output = subprocess.run(ffmpeg_command, stderr=subprocess.PIPE, text=True)
    if output.returncode != 0:
        print("FFmpeg Error:", output.stderr)

    end_time = time.time()

    duration = end_time - start_time
    formatted_duration = format_duration(duration)

    log_message(
        f"{fg('green')}Timelapse video created{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{video_path}{attr('reset')}")
    log_message(
        f"{fg('green')}Duration{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{formatted_duration}")
