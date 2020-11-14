#!/usr/bin/python3

import RPi.GPIO as GPIO
import time, math

GPIO.setmode(GPIO.BOARD)

rightMotorGPIOPins = [15, 13, 11, 7]
leftMotorGPIOPins = [10, 12, 16, 18]

# set all GPIOs to 0
def setGPIOsAsOutputAndTo0():
    for pin in leftMotorGPIOPins, rightMotorGPIOPins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

setGPIOsAsOutputAndTo0()

halfSteppinglPhase = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],    
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# assume motors are in these positions (out of 8 half steps in a cycle - so possibly off by 4) 
# Surely not true, but with 4096 steps, acceptable approximation
rightMotorCurrentStep = 0
leftMotorCurrentStep = 0

def turnMotorByHalfStepping(numberOfHalfSteps, pinsToBeActivated):

    # =======================================
    #TODO learn Python and refactor that properly - likely by building a motor class and passing an instance
    global rightMotorCurrentStep
    global leftMotorCurrentStep

    if pinsToBeActivated == rightMotorGPIOPins:
        currentStep = rightMotorCurrentStep
        rightMotorCurrentStep += numberOfHalfSteps
    else:
        currentStep = leftMotorCurrentStep
        leftMotorCurrentStep += numberOfHalfSteps
    # =======================================

    # rotate
    increment = 1 if numberOfHalfSteps > 0 else -1
    for _ in range(abs(numberOfHalfSteps)):

        currentStep = (currentStep + 8 + increment) % 8
        for pin in range(4):
            GPIO.output(pinsToBeActivated[pin], halfSteppinglPhase[currentStep][pin])
    
        # 0.0007 is the lower limit for a halfstep - after that coils dont have time to establish the mag field - maybe?
        time.sleep(0.5007)
        
# test :
turnMotorByHalfStepping(+20,leftMotorGPIOPins)
turnMotorByHalfStepping(-20,leftMotorGPIOPins)
turnMotorByHalfStepping(-20,rightMotorGPIOPins)
turnMotorByHalfStepping(+20,rightMotorGPIOPins)

# diameter 7.5mm :
pulleyPerimeter = 23.56 #mm
def turnMotors(stringDistanceLeftMotor, stringDistanceRightMotor):
    
    leftSteps = int(stringDistanceLeftMotor*4096/pulleyPerimeter)
    rightSteps = int(stringDistanceRightMotor*4096/pulleyPerimeter)

    # get around painful edge cases
    leftSteps = 1 if leftSteps == 0 else leftSteps
    rightSteps = 1 if rightSteps == 0 else rightSteps
     
    # implement Bresenham's algo here
    slope = abs(rightSteps/leftSteps)
    roundedSlope = int(slope)
    deviationPerLoop = abs(slope - roundedSlope)
    currentDeviation = 0

    for _ in range(0, abs(leftSteps)):

        # turn left by 1
        turnMotorByHalfStepping(1 if leftSteps>0 else -1, leftMotorGPIOPins)

        # turn right by slope
        turnMotorByHalfStepping(roundedSlope if rightSteps>0 else - roundedSlope, rightMotorGPIOPins)
        currentDeviation += deviationPerLoop

        # adjust current deviation if over 1
        while currentDeviation > 1:
            turnMotorByHalfStepping(1 if rightSteps>0 else -1, rightMotorGPIOPins)
            currentDeviation -= 1

# turnMotors(20, 20)

#########################################################
# distance between the two motors
halfDistanceBetweenMotors = 285 #mm

# initial position
x0 = 0
y0 = 290

def move(x1,y1):

    # current pen position :
    global x0, y0

    # calculate the distance of string to be rolled per motor
    # turn left motor by ?
    stringDistanceLeftMotor = math.sqrt(y1**2+(halfDistanceBetweenMotors+x1)**2) - math.sqrt(y0**2+(halfDistanceBetweenMotors+x0)**2)
    print("distance left motor : ", stringDistanceLeftMotor)

    # turn right motor by ?
    stringDistanceRightMotor = math.sqrt(y1**2+(halfDistanceBetweenMotors-x1)**2) - math.sqrt(y0**2+(halfDistanceBetweenMotors-x0)**2)
    print("distance right motor : ", stringDistanceRightMotor)

    turnMotors(stringDistanceLeftMotor,stringDistanceRightMotor)
    
    x0,y0 = x1,y1 # update current pen position
    print("Head now positioned at ",x0,y0)
#########################################################

# move(-40, 330)
# move(40, 330)
# reset to 0 post move / ok as everything is sequential

setGPIOsAsOutputAndTo0()

GPIO.cleanup()
