#!/bin/bash
# sudo cp send_photo.cgi /usr/lib/cgi-bin 
echo "Content-type: text/plain"
echo ""

# Base directory path
base_path="/var/www/html/images/"

# Today's date
year=$(date +"%Y")
month=$(date +"%m")
day=$(date +"%d")

# Construct today's directory path
today_path="${base_path}${year}/${month}/${day}"

# Get the most recent photo file (assuming .jpg extension, adjust if necessary)
latest_photo=$(ls -t ${today_path}/*.jpg | head -n 1)

# Endpoint and token details
laravel_endpoint="https://ekstremedia.no/api/getImageFromPi"
bearer_token=""
camera_id=""

# CURL command to send the photo
command="curl -X POST -H \"Authorization: Bearer $bearer_token\" -F \"photo=@$latest_photo\" -F \"camera=$camera_id\" $laravel_endpoint"
eval $command

echo "Photo from ${latest_photo} sent."

