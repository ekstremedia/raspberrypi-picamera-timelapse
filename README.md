## Raspberry Pi Timelapse
Copy `example.config.yaml` to `config.yaml` and edit it to your specifications.

`python capture_image.py` takes the photos and put on the overlay made in `overlay.py`

run `python create-timelapse.py` to create a timelapse of yesterday's video.

Or specify a date:

`python create-timelapse.py  --date 2023-06-09`

To create a test timelapse: 

`create-timelapse.py --date 2023-06-09 --dont-upload --debug`

Will create `/var/www/html/public/video-debug/2023_06_09_1920_1160_23.mp4`

Too see video specs:

ffprobe -i /var/www/html/public/video-debug/2023_06_09_1920_1160_23.mp4

or `create-timelapse.py 2023/06/10` to make a timelapse of a certain date

To create a day slice image:

`scripts/daylineImage.py --folder /var/www/html/images/2023/06/17 --date 2023-06-17 --slices 24`

Will be created in `temp/dayline-2023-06-17.jpg`

To test upload a video:

`python scripts/upload-timelapse-video.py --file /var/www/html/videos/2023/06/timelapse_2023_06_16.mp4 --date 2023-06-16`
