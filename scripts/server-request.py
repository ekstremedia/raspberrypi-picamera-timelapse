import requests
import yaml
import os
import sys
from new_logger import Logger

# Create a logger instance with a specific log file
logger = Logger('server-request.log')

# Add the directory containing your script to the Python path
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(script_dir)

def load_config():
    config_path = os.path.join(script_dir, '../config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def send_request(config, endpoint, payload=None):
    try:
        full_url = config['remote']['url'] + endpoint
        headers = {'Authorization': f'Bearer {config["remote"]["token"]}'}
        
        # Include camera_id in the payload
        if payload is None:
            payload = {}
        payload['camera_id'] = config['camera_id']

        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.log_message(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logger.log_message(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logger.log_message(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logger.log_message(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        logger.log_message(f"JSON decode error: {json_err}")
    return None

def reboot_system():
    # os.system('sudo reboot')
    logger.log_message("Rebooting")  # Use your custom logger for logging

def main():
    logger.log_message("Starting server request script")
    config = load_config()

    # Send initial request to the server
    response = send_request(config, '/api/piRequest')
    if response is None:
        logger.log_message("No response or error on initial request")
        return

    # Check the action from the response
    action = response.get('action', 'none')
    if action == 'reboot':
        logger.log_message("Received reboot command")

        # Acknowledge the reboot command
        ack_response = send_request(config, '/api/piRequestAnswer', {'reboot_acknowledged': True})
        if ack_response and ack_response.get('status') == 'success':
            logger.log_message("Reboot command acknowledged, proceeding to reboot")
            reboot_system()
        else:
            logger.log_message("Failed to acknowledge reboot command")
    else:
        logger.log_message(f"No action or unrecognized action: {action}")

if __name__ == "__main__":
    main()
