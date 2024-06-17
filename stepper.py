#!/usr/bin/python3
# coding=UTF-8
import RPi.GPIO as GPIO
import time, math, sys

from points_file_reader import read_file
from motor_control import turnMotorByHalfStepping, set_gpio_as_output_and_to_0
from motor_side import MotorSide  # Import the enum


GPIO.setmode(GPIO.BOARD)

set_gpio_as_output_and_to_0()

        
# test :
turnMotorByHalfStepping(+10,MotorSide.LEFT)
turnMotorByHalfStepping(-10,MotorSide.LEFT)
turnMotorByHalfStepping(+10,MotorSide.RIGHT)
turnMotorByHalfStepping(-10,MotorSide.RIGHT)

# turnMotorByHalfStepping(10000,rightMotorGPIOPins)
# turnMotorByHalfStepping(10000,leftMotorGPIOPins)




# inner diameter where the thread is : 7.5mm :
pulleyPerimeter = 23.56 #mm
def turnMotors(stringDistanceLeftMotor, stringDistanceRightMotor):
    
    leftSteps = int(stringDistanceLeftMotor*4096/pulleyPerimeter)
    rightSteps = int(stringDistanceRightMotor*4096/pulleyPerimeter)

    if rightSteps == 0:
        turnMotorByHalfStepping(leftSteps, MotorSide.LEFT)
        return

    # implement Bresenham's algo so we go roughly 
    # straight between the points
    # and faster by activating both motors at the same time
    slope = abs(stringDistanceLeftMotor/stringDistanceRightMotor)
    rounded_slope = int(slope)

    # turn right one step
    # turn left by int(slope)
    # accumulate deviation
    # while deviation>1 -> take a right step and decrement deviation 

    current_deviation = 0
    for _ in range(0, abs(rightSteps)):

        # turn right motor by one step
        turnMotorByHalfStepping(int(math.copysign(1,rightSteps)), MotorSide.RIGHT)
        # print("Right step ", math.copysign(1,rightSteps))

        # turn left by slope
        turnMotorByHalfStepping(int(rounded_slope * math.copysign(1,leftSteps)), MotorSide.LEFT)
        # print("Left step ", rounded_slope * math.copysign(1,leftSteps))
        
        current_deviation += (slope - rounded_slope)
        # print("Deviation ", current_deviation)

        # adjust until deviation is < 1 step
        while current_deviation > 1 :
            turnMotorByHalfStepping(int(math.copysign(1,leftSteps)), MotorSide.LEFT)
            current_deviation -= 1
            # print("Absorbing deviation - current ", current_deviation, "after left step ", int(math.copysign(1,leftSteps)))


# test : both motors should let go 10mm of string

# turnMotors(3, 1)
# turnMotors(1, 3)

# turnMotors(3, -1)
# turnMotors(1, -3)

# turnMotors(-3, 1)
# turnMotors(-1, 3)

# turnMotors(-3, -1)
# turnMotors(-1, -3)



#########################################################
# distance between the two motors
halfDistanceBetweenMotors = 285 #mm
pen_to_wood_bar_vertical_distance = 320 #mm

# initial position
x0 = 0
y0 = 0

def move(x1,y1):

    # current pen position :
    global x0, y0

    print("going from ",x0,y0," to ",x1,y1)

    # calculate the distance of string to be rolled per motor
    # turn left motor by ?
    stringDistanceLeftMotor = math.sqrt((pen_to_wood_bar_vertical_distance - y1)**2 + (halfDistanceBetweenMotors+x1)**2) - math.sqrt((pen_to_wood_bar_vertical_distance - y0)**2+(halfDistanceBetweenMotors+x0)**2)
    # print("distance left motor : ", stringDistanceLeftMotor)

    # turn right motor by ?
    stringDistanceRightMotor = math.sqrt((pen_to_wood_bar_vertical_distance - y1)**2+(halfDistanceBetweenMotors-x1)**2) - math.sqrt((pen_to_wood_bar_vertical_distance - y0)**2+(halfDistanceBetweenMotors-x0)**2)
    # print("distance right motor : ", stringDistanceRightMotor)

    turnMotors(stringDistanceLeftMotor,stringDistanceRightMotor)
    
    x0,y0 = x1,y1 # update current pen position
    print("Head now positioned at ",x0,y0)
#########################################################

# turnMotors(5,10)

# Actual execution of code :

# instructions = read_file(str(sys.argv[1]))

# for instruction in instructions:
#    move(instruction[0],instruction[1])

set_gpio_as_output_and_to_0()

GPIO.cleanup()
