#!/usr/bin/python
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import yaml
import googleapiclient.errors
import logging
import socket
from google.auth import exceptions
from google.oauth2 import service_account

# Set up logging
def setup_logging(config):
    if config.get('log_youtube_upload'):
        log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'youtube-upload.log')
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        return True
    else:
        return False

# Load configuration from yaml file
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def upload_video(filename, title, description, category_id, privacy_status, playlist_id, logging_enabled):
    try:
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

        script_dir = os.path.dirname(os.path.realpath(__file__))
        SERVICE_ACCOUNT_FILE = os.path.join(script_dir, 'oauth2.json')

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": category_id,
                    "description": description,
                    "title": title
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            },
            media_body=filename
        )

        response = request.execute()
        if logging_enabled:
            logging.info(f"Uploaded video with filename {filename}")
            logging.info(response)

        # Get the videoId from the response
        video_id = response['id']

        # Add the video to the playlist
        add_to_playlist(youtube, playlist_id, video_id, logging_enabled)
    except socket.timeout:
        if logging_enabled:
            logging.error("Socket timeout occurred during the video upload process.")
    except exceptions.RefreshError:
        if logging_enabled:
            logging.error("Authentication error (401) occurred during the video upload process.")

def add_to_playlist(youtube, playlist_id, video_id, logging_enabled):
    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )

        response = request.execute()
        if logging_enabled:
            logging.info(f"Added video with id {video_id} to playlist with id {playlist_id}")
            logging.info(response)
    except socket.timeout:
        if logging_enabled:
            logging.error("Socket timeout occurred during the playlist addition process.")
    except exceptions.RefreshError:
        if logging_enabled:
            logging.error("Authentication error (401) occurred during the playlist addition process.")

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3]
    category_id = "22"  # replace as per your requirements
    privacy_status = "public"  # or "public" or "unlisted"
    playlist_id = "PLl4QUohU2aB5oa0VycZb6H3hLPefErPK2"  # replace with your playlist ID
    config = load_config()
    logging_enabled = setup_logging(config)
    upload_video(filename, title, description, category_id, privacy_status, playlist_id, logging_enabled)
