from picamera2 import Picamera2
from time import sleep


class Camera:
    def __init__(self, resolution, framerate):
        self.camera = PiCamera2()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        config = self.picam.create_preview_configuration()
        self.picam.configure(config)


    def record(self, duration):
        # self.camera.start_recording('./video.h264')
        # sleep(duration)  # recording duration
        # self.camera.stop_recording()
        self.picam.start()
        time.sleep(2)
        self.picam.capture_file("test-python.jpg")