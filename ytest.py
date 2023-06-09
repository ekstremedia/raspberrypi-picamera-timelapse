#!/usr/bin/python
import subprocess

def test_youtube_upload():
    filename = "/var/www/html/videos/2023/06/timelapse_2023_06_13.mp4"
    title = "Test Video 2"
    description = "This is a test video for the YouTube uploader."

    upload_command = ['python', 'youtube-upload.py', filename, title, description]
    subprocess.run(upload_command, check=True)

if __name__ == "__main__":
    test_youtube_upload()
