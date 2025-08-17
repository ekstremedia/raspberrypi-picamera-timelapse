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

def ffmpeg_command(video_path, config, image_paths):
    """
    image_paths: list of ABSOLUTE paths to jpg files, already in the desired order.
    Returns True on success, False on failure.
    """
    # Guard: no frames
    if not image_paths:
        log_message(f"{fg('red')}No images provided to FFmpeg.{attr('reset')}")
        return False

    # Where to write the list file
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    list_path = os.path.join(data_dir, 'ffmpeg_list.txt')

    # Write concat list with absolute paths
    with open(list_path, 'w') as f:
        for p in image_paths:
            f.write(f"file '{p}'\n")

    # Read video settings with sane fallbacks
    width  = str(config['video_output'].get('video_width', 3840))
    height = str(config['video_output'].get('video_height', 2160))
    # Support both 'framerate' and 'frames_per_second' keys
    fr = str(config['video_output'].get('framerate', config['video_output'].get('frames_per_second', 25)))
    crf = str(config['video_output'].get('constant_rate_factor', 22))
    br  = str(config['video_output'].get('bitrate', 10000000))
    codec = (config['video_output'].get('codec') or 'libx264')

    # Hardware codec needs pixel format
    pix_fmt_args = []
    if codec == 'h264_v4l2m2m':
        pix_fmt_args = ['-pix_fmt', 'yuv420p']

    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_path,
        '-framerate', fr,
        '-s', f"{width}x{height}",
        '-vf', 'deflicker,setpts=N/FRAME_RATE/TB',
        '-c:v', codec,
        '-crf', crf,
        '-b:v', br,
        *pix_fmt_args,
        video_path
    ]

    # Display FFmpeg information settings
    log_message(f"{fg('green')}FFmpeg Information Settings{attr('reset')}")
    for flag, val in [('-f','concat'), ('-safe','0'), ('-i', list_path), ('-framerate', fr),
                      ('-s', f"{width}x{height}"), ('-vf', 'deflicker,setpts=N/FRAME_RATE/TB'),
                      ('-c:v', codec), ('-crf', crf), ('-b:v', br)] + ([('-pix_fmt','yuv420p')] if pix_fmt_args else []):
        log_message(f"{fg('cyan')}{flag} {attr('reset')}{fg(244)}{val}{attr('reset')}")

    log_message(f"{fg('green')}Starting timelapse...{attr('reset')}")

    start_time = time.time()
    proc = subprocess.run(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    end_time = time.time()
    duration = format_duration(end_time - start_time)

    if proc.returncode != 0:
        log_message(f"{fg('red')}FFmpeg Error{attr('reset')}: {proc.stderr}")
        return False

    log_message(f"{fg('green')}Timelapse video created{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{video_path}{attr('reset')}")
    log_message(f"{fg('green')}Duration{attr('reset')}{fg('dark_green')}: {attr('reset')}{fg(135)}{duration}")
    return True
