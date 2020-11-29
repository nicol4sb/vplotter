#!/usr/bin/python3
# coding=UTF-8
import RPi.GPIO as GPIO
import time, math

from points_file_reader import read_file

GPIO.setmode(GPIO.BOARD)

rightMotorGPIOPins = [15, 13, 11, 7]
leftMotorGPIOPins = [10, 12, 16, 18]

# set all GPIOs to 0
def set_gpio_as_output_and_to_0():
    for pin in leftMotorGPIOPins, rightMotorGPIOPins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

set_gpio_as_output_and_to_0()

halfSteppinglPhase = [
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1],    
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0]
]

# assume motors are in these positions (out of 8 half steps in a cycle - so off by 4 at the max)
# Surely not true, but with 4096 steps, acceptable approximation
rightMotorCurrentStep = 0
leftMotorCurrentStep = 0

def turnMotorByHalfStepping(numberOfHalfSteps, pinsToBeActivated):
    
    if numberOfHalfSteps == 0:
        return

    # =======================================
    #TODO Refactor
    global rightMotorCurrentStep
    global leftMotorCurrentStep

    # print("right current step", rightMotorCurrentStep, "left current step", leftMotorCurrentStep)

    if pinsToBeActivated == rightMotorGPIOPins:
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

        # print("Motor ", "right" if (pinsToBeActivated == rightMotorGPIOPins) else "left","current step ", current_step)
        
        # set pins so the appropriate step is activated
        for pin in range(4):
            GPIO.output(pinsToBeActivated[pin], halfSteppinglPhase[current_step][pin])
    
        # 0.0007 is the lower limit for a halfstep - after that coils dont have time to establish the mag field - maybe?
        time.sleep(0.0007)
        
# test :
# turnMotorByHalfStepping(+4,leftMotorGPIOPins)
# turnMotorByHalfStepping(-3,leftMotorGPIOPins)
# turnMotorByHalfStepping(+3,rightMotorGPIOPins)
# turnMotorByHalfStepping(-4,rightMotorGPIOPins)

# turnMotorByHalfStepping(100,rightMotorGPIOPins)
# turnMotorByHalfStepping(100,leftMotorGPIOPins)




# inner diameter where the thread is : 7.5mm :
pulleyPerimeter = 23.56 #mm
def turnMotors(stringDistanceLeftMotor, stringDistanceRightMotor):
    
    leftSteps = int(stringDistanceLeftMotor*4096/pulleyPerimeter)
    rightSteps = int(stringDistanceRightMotor*4096/pulleyPerimeter)

    if rightSteps == 0:
        turnMotorByHalfStepping(leftSteps, leftMotorGPIOPins)
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
        turnMotorByHalfStepping(int(math.copysign(1,rightSteps)), rightMotorGPIOPins)
        # print("Right step ", math.copysign(1,rightSteps))

        # turn left by slope
        turnMotorByHalfStepping(int(rounded_slope * math.copysign(1,leftSteps)), leftMotorGPIOPins)
        # print("Left step ", rounded_slope * math.copysign(1,leftSteps))
        
        current_deviation += (slope - rounded_slope)
        # print("Deviation ", current_deviation)

        # adjust until deviation is < 1 step
        while current_deviation > 1 :
            turnMotorByHalfStepping(int(math.copysign(1,leftSteps)), leftMotorGPIOPins)
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

# initial position
x0 = 0
y0 = 290

def move(x1,y1):

    # current pen position :
    global x0, y0

    print("going from ",x0,y0," to ",x1,y1)

    # calculate the distance of string to be rolled per motor
    # turn left motor by ?
    stringDistanceLeftMotor = math.sqrt(y1**2+(halfDistanceBetweenMotors+x1)**2) - math.sqrt(y0**2+(halfDistanceBetweenMotors+x0)**2)
    # print("distance left motor : ", stringDistanceLeftMotor)

    # turn right motor by ?
    stringDistanceRightMotor = math.sqrt(y1**2+(halfDistanceBetweenMotors-x1)**2) - math.sqrt(y0**2+(halfDistanceBetweenMotors-x0)**2)
    # print("distance right motor : ", stringDistanceRightMotor)

    turnMotors(stringDistanceLeftMotor,stringDistanceRightMotor)
    
    x0,y0 = x1,y1 # update current pen position
    print("Head now positioned at ",x0,y0)
#########################################################

# move(13,298)

# for each (x,y) in fileReader.readMoves(file)
#   move(x,y)
# DONE


instructions = read_file()

for instruction in instructions:
    move(instruction[0],instruction[1]+290)
    

set_gpio_as_output_and_to_0()

GPIO.cleanup()
