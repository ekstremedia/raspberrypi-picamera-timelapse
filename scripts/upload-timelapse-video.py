#!/usr/bin/python
import requests
import argparse
import os
import yaml
import logging
from colorlog import ColoredFormatter
import glob
from PIL import Image

def configure_logger():
    """Configure logger with colored output."""
    logger = logging.getLogger()
    
    # Configure stream handler for console
    stream_handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    # Configure file handler for log file
    log_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs', 'upload-timelapse-video.log')
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    logger.setLevel(logging.DEBUG)
    return logger


def create_thumbnail(image_file):
    """Create thumbnail from a selected image file."""
    with Image.open(image_file) as img:
        img.thumbnail((128, 128))
        thumbnail_file = f'{os.path.splitext(image_file)[0]}_thumbnail.jpg'
        img.save(thumbnail_file, "JPEG")
    return thumbnail_file

def main(file, date, thumbnail):
    # Load configuration file
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'config.yaml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    image_output_path = os.path.join(config['image_output']['root_folder'], date.replace('-', '/'))

    # If thumbnail not provided, select a random image file from the middle of the image directory
    if not thumbnail:
        image_files = sorted(glob.glob(f'{image_output_path}/*.jpg'))
        middle_image = image_files[len(image_files) // 2]
        thumbnail = create_thumbnail(middle_image)

    # Prepare data for POST request
    data = {
        'title': os.path.basename(file),
        'date': date
    }

    files = {
        'video': open(file, 'rb'),
        'thumbnail': open(thumbnail, 'rb'),
        'image': open(middle_image, 'rb')
    }

    # Prepare headers for the request
    headers = {
        'Authorization': f'Bearer {config["video_upload"]["api_key"]}',
    }

    # Send POST request to the server
    response = requests.post(config['video_upload']['url'], files=files, data=data, headers=headers)

    # Handle server response
    if response.status_code == 200:
        logger.info('File uploaded successfully.')
        logger.info(f'Response: {response.text}')
    else:
        logger.error(f'Failed to upload file. Server responded with status code {response.status_code}. Response body: {response.text}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload a timelapse video and thumbnail to a server.')
    parser.add_argument('--file', required=True, help='Path to the video file.')
    parser.add_argument('--date', required=True, help='Date of the video in YYYY-MM-DD format.')
    parser.add_argument('--thumbnail', required=False, help='Path to the thumbnail image file.')
    args = parser.parse_args()
    
    logger = configure_logger()

    main(args.file, args.date, args.thumbnail)
