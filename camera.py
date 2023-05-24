from picamera import PiCamera
from time import sleep


class Camera:
    def __init__(self, resolution, framerate):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate

    def record(self, duration):
        self.camera.start_recording('./video.h264')
        sleep(duration)  # recording duration
        self.camera.stop_recording()
