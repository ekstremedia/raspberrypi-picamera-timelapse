#!/usr/bin/python
import requests
import subprocess
import yaml
import os
import logging
from datetime import datetime, timedelta

# Dynamically find the project root directory
project_root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Setup logging
log_dir = os.path.join(project_root_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'checkUpload.log')

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.info(f"Logging to {log_file}")

# Load configuration
config_path = os.path.join(project_root_dir, 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Check if logging is enabled in config
log_check_upload = config.get('log_check_upload', False)

# Extract camera_id from configuration
camera_id = config['camera_id']

# Log configuration status
#if log_check_upload:
#    logging.info('Logging is enabled as per config.yaml')

# Get the remote URL from the config file
remote_url = config['remote']['url']

# Get today's date in the required format
current_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

# Define the endpoint URL
endpoint_url = f"{remote_url}/api/checkUploads?date={current_date}&camera_id={camera_id}"

try:
    # Log the request being sent
#    logging.info(f"Sending request to {endpoint_url}")

    # Send request to the server
    response = requests.get(endpoint_url)

    # Check server response
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('videoExists'):
                logging.info(f"Timelapse for {current_date} already exists.")
            else:
                logging.info(f"Timelapse for {current_date} does not exist. Creating timelapse.")
                command = ['python3', os.path.join(project_root_dir, 'create-timelapse.py'), '--date=' + current_date, '--only-upload']
                logging.info(f"Running command: {' '.join(command)}")
                subprocess.run(command)
        except ValueError:
            logging.error("Response content is not valid JSON")
    else:
        logging.error(f"Failed to check timelapse: {response.status_code} - {response.text}")

except requests.exceptions.RequestException as e:
    logging.error(f"Error connecting to server: {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")

