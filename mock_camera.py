from time import sleep


class MockCamera:
    def __init__(self, resolution, framerate):
        print(f"Mock Camera initialized with resolution: {resolution}, framerate: {framerate}")

    def record(self, duration):
        print(f"Mock Camera recording for {duration} seconds")
        sleep(duration)
        print("Mock Camera stopped recording")
