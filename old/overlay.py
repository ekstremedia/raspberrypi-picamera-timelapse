from PIL import Image, ImageDraw, ImageFont
import yaml
import os
import time
import math
import shutil
import sys
import logging
from getWeather import get_weather_data

# Load configuration from yaml file
def load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config

# Set up logging
def setup_logging(config):
    if config.get('log_overlay'):
        log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'capture-image.log')
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        return True
    else:
        return False
    
# Create gradient for overlay
def create_gradient(draw, width):
    for y in range(80):
        r, g, b = 0, 0, 40 + int((64 / 80) * y)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

# Draw overlay with camera name
def draw_overlay(draw, width, config):
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    text = f"{config['camera_name']}"
    text_x = (width - draw.textbbox(xy=(0, 0), text=text, font=font)[2]) // 2 + 20
    text_y = 5
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

def draw_date(draw, width):
    date_text = time.strftime('%Y-%m-%d %H:%M:%S')
    date_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    date_x = (width - draw.textbbox(xy=(0, 0), text=date_text, font=date_font)[2]) // 2 + 20
    date_y = 48
    draw.text((date_x, date_y), date_text, font=date_font, fill=(255, 255, 255))
    
# Draw date on overlay
def draw_date(draw, width):
    date_text = time.strftime('%Y-%m-%d %H:%M:%S')
    date_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    date_x = (width - draw.textbbox(xy=(0, 0), text=date_text, font=date_font)[2]) // 2 + 20
    date_y = 48
    draw.text(xy=(date_x, date_y), text=date_text, font=date_font, fill=(255, 255, 255))

# Draw weather icon on overlay
def draw_weather_icon(new_img, weather_data, width):
    symbol = weather_data.get('symbol')
    weather_icon_path = f"/home/pi/raspberrypi-picamera-timelapse/yrimg/{symbol}.png"

    if os.path.isfile(weather_icon_path):
        weather_icon = Image.open(weather_icon_path).convert('RGBA')
        transparent_icon = Image.new('RGBA', weather_icon.size, (255, 255, 255, 0))
        transparent_icon.paste(weather_icon, (0, 0), weather_icon)
        transparent_icon = transparent_icon.resize((60, 60))

        icon_x = 10
        icon_y = (70 - transparent_icon.height) // 2
        new_img.paste(transparent_icon, (icon_x, icon_y), transparent_icon)

def draw_weather_data(draw, weather_data):
    # Define the starting point and spacing for the weather data
    data_x = 80
    data_y = 11
    data_spacing = 22

    # Check if weather data is available
    if weather_data:
        # Extract the necessary weather data
        temperature = f"{weather_data['02:00:00:5f:3f:f8']['Temperature']}°C"
        wind_speed = f"{weather_data['06:00:00:05:7b:ca']['WindStrength']} m/s"
        wind_direction = int(weather_data['06:00:00:05:7b:ca']['WindAngle'])
        rain = f"{weather_data['05:00:00:06:5f:30']['Rain']} mm"

        # Define the font for the weather data
        data_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)

        # Draw the weather data on the image
        draw.text((data_x, data_y), f"Temperatur: {temperature}", font=data_font, fill=(255, 255, 255))
        wind_line = f"Vind: {wind_speed} fra {wind_direction}°"
        draw.text((data_x, data_y + data_spacing), wind_line, font=data_font, fill=(255, 255, 255))
        draw.text((data_x, data_y + 2 * data_spacing), f"Nedbør: {rain}", font=data_font, fill=(255, 255, 255))

        # Draw the wind direction arrow
        draw_wind_direction_arrow(draw, data_x, data_y, data_spacing, wind_line, data_font, wind_direction)

def draw_wind_direction_arrow(draw, data_x, data_y, data_spacing, wind_line, data_font, wind_direction):
    # Define the starting point for the arrow
    arrow_x = data_x + draw.textbbox((data_x, data_y + data_spacing), wind_line, font=data_font)[2] + 70
    arrow_y = data_y + data_spacing + 12

    # Define the angle, length, and width of the arrow
    angle = math.radians(90 + int(wind_direction))
    arrow_length = 20
    arrow_width = 6

    # Adjust the starting point for the arrow if the wind direction is 180 degrees
    if wind_direction == "180":
        arrow_y -= arrow_length

    # Calculate the points for the arrow
    center_x = arrow_x
    center_y = arrow_y + arrow_length
    x1 = center_x + arrow_length * math.cos(angle)
    y1 = center_y + arrow_length * math.sin(angle)
    x2 = center_x - arrow_width * math.cos(angle + math.pi / 2)
    y2 = center_y - arrow_width * math.sin(angle + math.pi / 2)
    x3 = center_x - arrow_width * math.cos(angle - math.pi / 2)
    y3 = center_y - arrow_width * math.sin(angle - math.pi / 2)

    # Draw the arrow on the image
    draw.polygon([(x1, y1 - arrow_length), (x2, y2 - arrow_length), (x3, y3 - arrow_length)], fill=(255, 255, 255))

def add_overlay(config, image_path, weather_data):
    # Open the image and get its size
    img = Image.open(image_path)
    width, height = img.size

    # Create a new image with additional height for the overlay
    new_height = height + 80
    new_img = Image.new('RGB', (width, new_height), (255, 255, 255))
    new_img.paste(img, (0, 80))

    # Create a draw object for the new image
    draw = ImageDraw.Draw(new_img)

    # Draw the gradient, overlay, and date on the new image
    create_gradient(draw, width)
    draw_overlay(draw, width, config)
    draw_date(draw, width)

    # Attempt to draw the weather icon and data on the new image
    try:
        draw_weather_icon(new_img, weather_data, width)
        draw_weather_data(draw, weather_data)
    except Exception as e:
        print(f"Failed to load weather data: {e}")

    # Save the new image and copy it to the status file location
    new_img.save(image_path)
    shutil.copy2(image_path, config['status_file'])

if __name__ == "__main__":
    # Load the configuration file
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')

    # Set up logging
    logging_enabled = setup_logging(config)

    # Get the image path from the command line arguments
    image_path = sys.argv[1]

    # Log the image path
    if logging_enabled:
        logging.info(f"Image path: {image_path}")

    # Attempt to get the weather data
    try:
        weather_data = get_weather_data()
        if logging_enabled:
            logging.info("Weather data retrieved successfully.")
    except Exception as e:
        print(f"Failed to get weather data: {e}")
        weather_data = None
        if logging_enabled:
            logging.error(f"Failed to get weather data: {e}")

    # Add the overlay to the image
    try:
        add_overlay(config, image_path, weather_data)
        if logging_enabled:
            logging.info("Overlay added successfully.")
    except Exception as e:
        print(f"Failed to add overlay: {e}")
        if logging_enabled:
            logging.error(f"Failed to add overlay: {e}")