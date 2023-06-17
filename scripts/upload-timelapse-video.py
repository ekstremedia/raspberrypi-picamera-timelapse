#!/usr/bin/python
import requests
import argparse
import os
import yaml
import logging
from colorlog import ColoredFormatter
import glob
from PIL import Image
from daylineImage import create_dayline_image

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


def create_thumbnail(image_file, resize=False):
    """Create thumbnail from a selected image file."""
    with Image.open(image_file) as img:
        thumbnail_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'temp')
        os.makedirs(thumbnail_folder, exist_ok=True)  # Create the "temp" folder if it doesn't exist
        if resize:
            thumbnail_file = os.path.join(thumbnail_folder, 'thumbnail.jpg')
            img.thumbnail((512, 512))
            img.save(thumbnail_file, "JPEG")
        else:
            thumbnail_file = os.path.join(thumbnail_folder, 'image.jpg')
            img.save(thumbnail_file, "JPEG", quality=60)
        
    return thumbnail_file


def main(file, date, thumbnail):
    # Load configuration file
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'config.yaml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    image_output_path = os.path.join(config['image_output']['root_folder'], date[:4], date[5:7], date[8:])

    # Check if image files are available
    image_files = sorted(glob.glob(f'{image_output_path}/*.jpg'))
    if not image_files:
        logger.error(f"No image files found in the directory: {image_output_path}")
        return

    # If thumbnail not provided, select a random image file from the middle of the image directory
    if not thumbnail:
        middle_image = image_files[len(image_files) // 2]

        thumbnail = create_thumbnail(middle_image, resize=True)
        regular_image = create_thumbnail(middle_image)

        # Update the files dictionary with the correct middle image file
        files = {
            'video': open(file, 'rb'),
            'thumbnail': open(thumbnail, 'rb'),
            'image': open(regular_image, 'rb')
        }
    else:
        # Only the video and thumbnail files are provided
        files = {
            'video': open(file, 'rb'),
            'thumbnail': open(thumbnail, 'rb'),
            'image': open(regular_image, 'rb')
        }

    try:
        # Create the daylight image
        dayline_image_path = create_dayline_image(image_output_path, 24)

        # Use the daylight image as 'daylight' in the files dictionary
        files['daylight'] = open(dayline_image_path, 'rb')
    except Exception as e:
        logger.error(f'Failed to create daylight image. Error: {str(e)}')

    # Prepare data for POST request
    data = {
        'title': os.path.basename(file),
        'date': date
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
    parser.add_argument('--date', required=False, help='Date of the video in YYYY-MM-DD format.')
    parser.add_argument('--thumbnail', required=False, help='Path to the thumbnail image file.')
    args = parser.parse_args()

    logger = configure_logger()

    if not args.date:
        # Extract the date from the --file argument if --date is not provided
        filename = os.path.basename(args.file[-14:-4])
        # print(filename[-14:-4])
        date = filename.replace('_', '-')
    else:
        date = args.date

    main(args.file, date, args.thumbnail)
