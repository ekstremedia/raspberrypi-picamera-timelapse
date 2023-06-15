import os
import psutil
import subprocess
from datetime import datetime

def get_cpu_temperature():
    try:
        temperatures = psutil.sensors_temperatures()
        for name, entries in temperatures.items():
            for entry in entries:
                if entry.label == 'CPU':
                    return entry.current
    except ImportError:
        pass

    try:
        result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
        temperature_string = result.stdout.strip()
        temperature_value = temperature_string.split('=')[1].split('\'')[0]
        return temperature_value
    except (FileNotFoundError, IndexError):
        return None

def get_memory_usage():
    mem_info = psutil.virtual_memory()
    total_memory = mem_info.total
    used_memory = mem_info.used
    memory_percent = mem_info.percent
    return {
        "Total Memory": total_memory,
        "Used Memory": used_memory,
        "Memory Usage Percentage": memory_percent
    }

def get_disk_usage():
    disk_info = psutil.disk_usage('/')
    total_space = disk_info.total
    used_space = disk_info.used
    free_space = disk_info.free
    usage_percent = disk_info.percent
    return {
        "Total Disk Space": total_space,
        "Used Disk Space": used_space,
        "Free Disk Space": free_space,
        "Disk Usage Percentage": usage_percent
    }

def get_load_averages():
    with open('/proc/loadavg', 'r') as file:
        load_avg_values = file.read().split()[:3]
    return ", ".join(load_avg_values)

def format_size(size_in_bytes):
    power = 2 ** 10
    n = 0
    size_labels = ["bytes", "KB", "MB", "GB", "TB"]
    while size_in_bytes > power:
        size_in_bytes /= power
        n += 1
    return f"{size_in_bytes:.2f} {size_labels[n]}"

def get_photos_captured_today():
    today = datetime.now().strftime("%Y/%m/%d")
    photos_folder = f"/var/www/html/images/{today}"
    
    if not os.path.exists(photos_folder):
        return 0, 0

    photo_files = [f for f in os.listdir(photos_folder) if os.path.isfile(os.path.join(photos_folder, f))]
    num_photos = len(photo_files)
    total_size = sum(os.path.getsize(os.path.join(photos_folder, f)) for f in photo_files)

    return num_photos, total_size

def get_pi_data():
    data = {}
    data["CPU Temperature"] = get_cpu_temperature()
    memory_usage = get_memory_usage()
    for key, value in memory_usage.items():
        if key == "Memory Usage Percentage":
            data[key] = f"{value:.2f}%"
        else:
            data[key] = format_size(value)

    disk_usage = get_disk_usage()
    for key, value in disk_usage.items():
        if key == "Disk Usage Percentage":
            data[key] = f"{value:.2f}%"
        else:
            data[key] = format_size(value)

    data["Load Average"] = get_load_averages()

    num_photos, total_size = get_photos_captured_today()
    data["Photos Captured Today"] = num_photos
    data["Total Size of Photos"] = format_size(total_size)

    return data

if __name__ == "__main__":
    pi_data = get_pi_data()
    for key, value in pi_data.items():
        print(f"{key}: {value}")

