# gpio_utils.py
import RPi.GPIO as GPIO

rightMotorGPIOPins = [15, 13, 11, 7]
leftMotorGPIOPins = [10, 12, 16, 18]

# Set all GPIOs to 0
def set_gpio_as_output_and_to_0():
    for pin_group in (leftMotorGPIOPins, rightMotorGPIOPins):
        for pin in pin_group:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
