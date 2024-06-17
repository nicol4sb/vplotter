import RPi.GPIO as GPIO
import time

from motor_side import MotorSide  # Import the enum

__rightMotorGPIOPins = [15, 13, 11, 7]
__leftMotorGPIOPins = [10, 12, 16, 18]
__halfSteppinglPhase = [
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1],    
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0]
]

# Set all GPIOs to 0
def set_gpio_as_output_and_to_0():
    for pin_group in (__leftMotorGPIOPins, __rightMotorGPIOPins):
        for pin in pin_group:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

# assume motors are in these positions (out of 8 half steps in a cycle - so off by 4 at the max)
# Surely not true, but with 4096 steps, acceptable approximation
rightMotorCurrentStep = 0
leftMotorCurrentStep = 0


def turnMotorByHalfStepping(numberOfHalfSteps, motorSide):
    
    if numberOfHalfSteps == 0:
        return

    # =======================================
    #TODO Refactor
    global rightMotorCurrentStep
    global leftMotorCurrentStep

    # print("right current step", rightMotorCurrentStep, "left current step", leftMotorCurrentStep)

    if motorSide == MotorSide.RIGHT:
        current_step = rightMotorCurrentStep
        rightMotorCurrentStep += numberOfHalfSteps

    else:
        current_step = leftMotorCurrentStep
        leftMotorCurrentStep += numberOfHalfSteps
    # =======================================

    # rotate
    increment = 1 if numberOfHalfSteps>0 else -1
    for _ in range(abs(numberOfHalfSteps)):

        # go through the steps so that a positive number of steps equals a string extension on the pulley
        current_step = (current_step + 8 + increment) % 8

        print("Motor ", "right" if (motorSide == MotorSide.RIGHT) else "left","current step ", current_step)
        
        # set pins so the appropriate step is activated
        for pin in range(4):
            GPIO.output(motorSide == __rightMotorGPIOPins[pin] if MotorSide.RIGHT else __leftMotorGPIOPins[pin], __halfSteppinglPhase[current_step][pin])
    
        # 0.0007 is the lower limit for a halfstep - after that coils dont have time to establish the mag field - maybe?
        time.sleep(0.0007)