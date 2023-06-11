#!/usr/bin/python
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video(filename, title, description, category_id, privacy_status):
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "oauth2.json", scopes)
    credentials = flow.run_local_server(port=0)
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
