#!/usr/bin/python
from picamera2 import Picamera2
import time
picam2 = Picamera2()
#picam2.options["quality"] = 95
#picam2.options["compress_level"] = 2
picam2.start()
time.sleep(1)
picam2.capture_file("/var/www/html/test2.jpg")
