#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import yaml
import time

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
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)  # Increase the font size to 40
    text = f"{config['camera_name']}"
    text_width, text_height = draw.textsize(text, font=font)
    draw.text(((width - text_width) / 2, 10), text, font=font, fill=(255, 255, 255))  # Center the camera name vertically

    # Draw the date
    date_text = time.strftime('%Y-%m-%d %H:%M:%S')
    date_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    date_width, date_height = draw.textsize(date_text, font=date_font)
    draw.text(((width - date_width) / 2, 55), date_text, font=date_font, fill=(255, 255, 255))  # Center the date vertically

    # TODO: Add placeholders for weather and tide data

    # Save the new image
    new_img.save(image_path)

if __name__ == "__main__":
    import sys
    config = load_config('/home/pi/raspberrypi-picamera-timelapse/config.yaml')
    add_overlay(config, sys.argv[1])

