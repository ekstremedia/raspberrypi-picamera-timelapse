#!/usr/bin/python
import subprocess
import os
import yaml
from datetime import datetime, timedelta

# Read the config.yaml file
with open('../config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Calculate the previous month
last_month_date = datetime.now().replace(day=1) - timedelta(days=1)
folder_structure = last_month_date.strftime(config['video_output']['folder_structure'])
root_folder = config['video_output']['root_folder']
target_folder = os.path.join(root_folder, folder_structure)

# Get the video files and sort them
video_files = sorted([f for f in os.listdir(target_folder) if f.endswith('.mp4')])

# Create a temporary file listing all the videos to be concatenated
with open('file_list.txt', 'w') as file:
    for video_file in video_files:
        file.write(f"file '{os.path.join(target_folder, video_file)}'\n")

# # Use FFmpeg to concatenate the videos
# output_file = os.path.join(target_folder, f'timelapse_combined_{last_month_date.strftime("%Y_%m")}.mp4')
# subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'file_list.txt', '-c', 'copy', output_file])

# # Clean up the temporary file
# os.remove('file_list.txt')

# print(f"Combined video saved to {output_file}")


# Use FFmpeg to concatenate the videos
temporary_file = os.path.join(target_folder, 'timelapse_temp.mp4')
subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'file_list.txt', '-c', 'copy', temporary_file])

# Get the duration of the concatenated video
duration_command = ['ffmpeg', '-i', temporary_file, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv="p=0"']
duration = float(subprocess.run(duration_command, stdout=subprocess.PIPE).stdout.decode('utf-8'))

# Calculate the speed-up factor to make the video 1 minute long
speed_up_factor = duration / 60

# Apply the speed-up effect
output_file = os.path.join(target_folder, f'timelapse_combined_{last_month_date.strftime("%Y_%m")}.mp4')
subprocess.run(['ffmpeg', '-i', temporary_file, '-vf', f'setpts={speed_up_factor}*PTS', '-an', output_file])

# Clean up the temporary files
os.remove('file_list.txt')
os.remove(temporary_file)

print(f"Combined video saved to {output_file}")