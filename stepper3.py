import RPi.GPIO as GPIO
import time, math

GPIO.setmode(GPIO.BOARD)

rightMotorGPIOPins = [7, 11, 13, 15]
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

# assume motors are in these positions to start with 
# Surely not true, but with 4096 steps, acceptable approximation
rightMotorCurrentStep = 0
leftMotorCurrentStep = 0

def turnMotorByHalfStepping(numberOfHalfSteps, pinsToBeActivated):

    currentHalfstep = 0

    # rotate
    increment = 1 if numberOfHalfSteps > 0 else -1
    for _ in range(abs(numberOfHalfSteps)):
        for pin in range(4):
            GPIO.output(pinsToBeActivated[pin], halfSteppinglPhase[currentHalfstep][pin])
        currentHalfstep = (currentHalfstep + 8 + increment) % 8 # iterating over the 8 half steps
        time.sleep(0.0007)

turnMotorByHalfStepping(4096,leftMotorGPIOPins)
turnMotorByHalfStepping(4096,rightMotorGPIOPins)
turnMotorByHalfStepping(-4096,leftMotorGPIOPins)
turnMotorByHalfStepping(-4096,rightMotorGPIOPins)
setGPIOsAsOutputAndTo0()

def move(x0, y0, x1,y1):

    # distance between the two motors
    d = 290 #mm

    # calculate the distance of string to be rolled per motor
    # turn left motor by ?
    stringDistanceLeftMotor = math.sqrt(y1**2+(d+x1)**2) - math.sqrt(y0**2+(d+x0)**2)
    print("distance left motor : ", stringDistanceLeftMotor)

    # turn right motor by ?
    stringDistanceRightMotor = math.sqrt(y1**2+(d-x1)**2) - math.sqrt(y0**2+(d-x0)**2)
    print("distance right motor : ", stringDistanceRightMotor)

    turnMotors(stringDistanceLeftMotor,stringDistanceRightMotor)

# apply the Bresenham's algo to have a somewhat straight line
def turnMotors(stringDistanceLeftMotor, stringDistanceRightMotor):
    
    # implement Bresenham's algo here
    turnMotorByHalfStepping(int(stringDistanceLeftMotor/25*4096), leftMotorGPIOPins)
    turnMotorByHalfStepping(int(stringDistanceRightMotor/25*4096), rightMotorGPIOPins)


GPIO.cleanup()

