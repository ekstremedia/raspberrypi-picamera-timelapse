#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import yaml
import time
import math

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def add_overlay(config, image_path):
    # Open the image file
    img = Image.open(image_path)
    width, height = img.size

    # Create a new image with space for the overlay
    new_height = height + 80  # Increase the added space to 80px
    new_img = Image.new('RGB', (width, new_height), (255, 255, 255))
    new_img.paste(img, (0, 80))

    # Draw the gradient
    draw = ImageDraw.Draw(new_img)
    for y in range(80):
        r, g, b = 0, 0, 128 + int((64 / 80) * y)  # Calculate the blue value for the gradient
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Draw the overlay
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)  # Decrease the font size to 36
    text = f"{config['camera_name']}"
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (width - text_width) // 2 + 20  # Adjust the text position to the right
    draw.text((text_x, 10), text, font=font, fill=(255, 255, 255))  # Center the camera name vertically

    # Draw the date
    date_text = time.strftime('%Y-%m-%d %H:%M:%S')
    date_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    date_width, date_height = draw.textsize(date_text, font=date_font)
    date_x = (width - date_width) // 2 + 20  # Adjust the date position to the right
    draw.text((date_x, 55), date_text, font=date_font, fill=(255, 255, 255))  # Center the date vertically

    # Load the weather icon image and convert it to RGBA mode
    weather_icon_path = '/home/pi/raspberrypi-picamera-timelapse/yrimg/01d.png'  # Replace with the path to the weather icon image
    weather_icon = Image.open(weather_icon_path).convert('RGBA')

    # Create a blank image with a transparent background
    transparent_icon = Image.new('RGBA', weather_icon.size, (255, 255, 255, 0))

    # Composite the weather icon on the transparent background
    transparent_icon.paste(weather_icon, (0, 0), weather_icon)

    # Resize the transparent weather icon
    transparent_icon = transparent_icon.resize((60, 60))

    # Calculate the position for the weather icon
    icon_x = 10
    icon_y = (80 - transparent_icon.height) // 2  # Center the icon vertically

    # Overlay the transparent weather icon
    new_img.paste(transparent_icon, (icon_x, icon_y), transparent_icon)

    # Draw the weather data
    data_x = 80  # X coordinate for the weather data
    data_y = 11  # Y coordinate for the first line of weather data
    data_spacing = 22  # Spacing between each line of weather data

    temperature = "10°C"
    wind_speed = "2.5 m/s"
    wind_direction = "214"
    rain = "0 mm"

    data_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)  # Decrease the font size to 14
    draw.text((data_x, data_y), f"Temperature: {temperature}", font=data_font, fill=(255, 255, 255))
    wind_line = f"Wind: {wind_speed} from {wind_direction}°"
    draw.text((data_x, data_y + data_spacing), wind_line, font=data_font, fill=(255, 255, 255))
    draw.text((data_x, data_y + 2 * data_spacing), f"Rain: {rain}", font=data_font, fill=(255, 255, 255))

    arrow_x = data_x + draw.textsize(wind_line)[0] + 70  # Position the arrow at the end of the wind line
    arrow_y = data_y + data_spacing + 12  # Move the arrow down slightly

    # Draw the wind direction arrow
    angle = math.radians(90 + int(wind_direction))  # Add 90 degrees to rotate clockwise
    arrow_length = 20  # Adjust the length of the arrow
    arrow_width = 6  # Adjust the width of the arrow

    if wind_direction == "180":
        arrow_y -= arrow_length

    # Calculate the center point of the arrow
    center_x = arrow_x
    center_y = arrow_y + arrow_length

    # Calculate the coordinates of the arrow points relative to the center
    x1 = center_x + arrow_length * math.cos(angle)
    y1 = center_y + arrow_length * math.sin(angle)
    x2 = center_x - arrow_width * math.cos(angle + math.pi / 2)
    y2 = center_y - arrow_width * math.sin(angle + math.pi / 2)
    x3 = center_x - arrow_width * math.cos(angle - math.pi / 2)
    y3 = center_y - arrow_width * math.sin(angle - math.pi / 2)

    # Translate the coordinates to the absolute positions
    x1_abs = x1
    y1_abs = y1 - arrow_length
    x2_abs = x2
    y2_abs = y2 - arrow_length
    x3_abs = x3
    y3_abs = y3 - arrow_length

    draw.polygon([(x1_abs, y1_abs), (x2_abs, y2_abs), (x3_abs, y3_abs)], fill=(255, 255, 255))

    # Save the new image
    new_img.save(image_path)

if __name__ == "__main__":
    import sys
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    add_overlay(config, sys.argv[1])
