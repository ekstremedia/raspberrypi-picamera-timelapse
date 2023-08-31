import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://api.sunrise-sunset.org/json?lat=68.7252112&lng=15.4506372&formatted=0&date="

def fetch_sun_data(date_str):
    response = requests.get(BASE_URL + date_str)
    data = response.json()['results']
    return data

def process_data(data):
    sunrise, sunset, solar_noon = data['sunrise'], data['sunset'], data['solar_noon']

    if sunrise == "1970-01-01T00:00:01+00:00":
        sunrise = "never_rises"
    
    if sunset == "1970-01-01T00:00:01+00:00":
        sunset = "never_sets"

    return {
        "sunrise": sunrise,
        "sunset": sunset,
        "solar_noon": solar_noon
    }

def main():
    start_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2023-12-31", "%Y-%m-%d")
    delta = timedelta(days=1)

    result = {}

    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        date_key = start_date.strftime("%m-%d")
        
        sun_data = fetch_sun_data(date_str)
        processed_data = process_data(sun_data)
        
        result[date_key] = processed_data
        
        start_date += delta

    with open("sun_data_2023.json", "w") as file:
        json.dump(result, file, indent=4)

if __name__ == "__main__":
    main()

