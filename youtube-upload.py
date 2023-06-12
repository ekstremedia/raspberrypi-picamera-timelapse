#!/usr/bin/python
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.upload"]

from google.oauth2 import service_account

def upload_video(filename, title, description, category_id, privacy_status):
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    SERVICE_ACCOUNT_FILE = 'oauth2.json'

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
    print(response)


if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3]
    category_id = "22"  # replace as per your requirements
    privacy_status = "private"  # or "public" or "unlisted"
    upload_video(filename, title, description, category_id, privacy_status)
