#!/usr/bin/python3
# coding=UTF-8
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

try:
    while True:
        GPIO.output(16, 1)
        time.sleep(1)
        GPIO.output(16, 0)
        time.sleep(1)
finally:
    # Clean up GPIO settings
    GPIO.cleanup()
