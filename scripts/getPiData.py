#!/usr/bin/python
from piDataStats import get_pi_data

data = get_pi_data()

# Retrieve specific measurements
cpu_temperature = data["CPU Temperature"]
total_memory = data["Total Memory"]
used_memory = data["Used Memory"]
memory_usage_percentage = data["Memory Usage Percentage"]
total_disk_space = data["Total Disk Space"]
used_disk_space = data["Used Disk Space"]
free_disk_space = data["Free Disk Space"]
disk_usage_percentage = data["Disk Usage Percentage"]
load_averages = data["Load Average"]
photos_captured_today = data["Photos Captured Today"]
total_photo_size = data["Total Size of Photos"]

# # Use the retrieved data as needed
# print("CPU Temperature:", cpu_temperature)
# print("Total Memory:", total_memory)
# print("Used Memory:", used_memory)
# print("Memory Usage Percentage:", memory_usage_percentage)
# print("Total Disk Space:", total_disk_space)
# print("Used Disk Space:", used_disk_space)
# print("Free Disk Space:", free_disk_space)
# print("Disk Usage Percentage:", disk_usage_percentage)
# print("Load Averages:", load_averages)
# print("Photos Captured Today:", photos_captured_today)
# print("Total Size of Photos:", total_photo_size)

