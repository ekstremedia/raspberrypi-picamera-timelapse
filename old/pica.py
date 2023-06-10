from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

config = picam2.preview_configuration()
picam2.configure(config)

picam2.start()
