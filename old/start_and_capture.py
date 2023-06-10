#!/usr/bin/python

from picamera2 import Picamera2
picam2 = Picamera2()
filename = "/var/www/html/test.jpg"
picam2.start_and_capture_file(filename,delay=0,show_preview=False)

