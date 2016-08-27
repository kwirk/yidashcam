#!/usr/bin/env python
"""Put YI Dashcam in stream mode"""

import time

from . import YIDashcam

with YIDashcam() as yi:
    print("Model: {0.model}\n"
          "Serial Number: {0.serial_number}\n"
          "Firmware Version: {0.firmware_version}\n"
          "Connect to video stream at: rtsp://{0.HOST}/xxx.mov".format(yi))
    while yi.connected:
        time.sleep(0.1)
