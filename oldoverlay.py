from PIL import Image, ImageDraw, ImageFont
import sys
import time

def overlay_image(image_path):
    # Load the main image and create a draw object
    main_image = Image.open(image_path)
    draw = ImageDraw.Draw(main_image)

    # Define the font and font sizes
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    data_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)

    # Define the weather data
    temperature = "10°C"
    rain = "0 mm"
    wind_speed = "2.5 m/s"
    wind_direction = "243°"
    tide_water_level = "Max"
    tide_direction = "Up"

    # Define the position for the weather data
    data_x = 10  # X coordinate
    data_y = 60  # Y coordinate
    data_spacing = 25  # Spacing between each line of data

    # Overlay the camera name
    camera_name = "Camera Name"
    draw.text((10, 10), camera_name, font=title_font, fill=(255, 255, 255))

    # Overlay the date and time
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    draw.text((10, 50), current_time, font=data_font, fill=(255, 255, 255))

    # Overlay the weather image
    weather_image_path = "./yrimg/01d.png"  # Replace with the actual path to the weather image
    weather_image = Image.open(weather_image_path)
    main_image.paste(weather_image, (10, 100))

    # Overlay the weather data
    draw.text((data_x, data_y), f"Temperature: {temperature}", font=data_font, fill=(255, 255, 255))
    draw.text((data_x, data_y + data_spacing), f"Rain: {rain}", font=data_font, fill=(255, 255, 255))
    draw.text((data_x, data_y + 2 * data_spacing), f"Wind: {wind_speed} {wind_direction}", font=data_font, fill=(255, 255, 255))
    draw.text((data_x, data_y + 3 * data_spacing), f"Tide: {tide_water_level} {tide_direction}", font=data_font, fill=(255, 255, 255))

    # Save the modified image
    main_image.save(image_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python overlay.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    overlay_image(image_path)

