#!/usr/bin/python
import requests
import os
import time

CACHE_FOLDER = "cache"
CACHE_FILE = os.path.join(CACHE_FOLDER, "netatmo.json")
CACHE_EXPIRY = 300  # 5 minutes in seconds

def get_weather_data():
    # Check if cache file exists and is newer than 5 minutes
    if os.path.exists(CACHE_FILE) and time.time() - os.path.getmtime(CACHE_FILE) < CACHE_EXPIRY:
        with open(CACHE_FILE, "r") as file:
            return file.read()

    url = "https://ekstremedia.no/api/weather/getWeatherForPi"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        weather_data = response.text

        # Save the data to the cache file
        os.makedirs(CACHE_FOLDER, exist_ok=True)
        with open(CACHE_FILE, "w") as file:
            file.write(weather_data)

        return weather_data
    except requests.exceptions.RequestException as e:
        print("Failed to fetch weather data:", e)
        return None

weather_data = get_weather_data()

if weather_data is not None:
    # Process the weather data as needed
    print(weather_data)
