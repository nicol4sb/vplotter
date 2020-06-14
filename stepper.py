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



# assume motors are in these positions to start with 
# Surely not true, but with 4096 steps, acceptable approximation
rightMotorCurrentStep = 0
leftMotorCurrentStep = 0
currentHalfstep = 0 # this initialization is not too relevant - we will miss a few starting points possibly

def turnMotorByHalfStepping(numberOfHalfSteps, pinsToBeActivated):

    global currentHalfstep

    # rotate
    increment = 1 if numberOfHalfSteps > 0 else -1
    for _ in range(abs(numberOfHalfSteps)):

        currentHalfstep = (currentHalfstep + 8 + increment) % 8 # iterating over the 8 half steps

        for pin in range(4):
            GPIO.output(pinsToBeActivated[pin], halfSteppinglPhase[currentHalfstep][pin])

        time.sleep(0.0007)
        
        # reset to 0 post move / ok as everything is sequential
        setGPIOsAsOutputAndTo0()

# apply the Bresenham's algo to have a somewhat straight line
def turnMotors(stringDistanceLeftMotor, stringDistanceRightMotor):
    
    leftSteps = int(stringDistanceLeftMotor*4096/25)
    rightSteps = int(stringDistanceRightMotor*4096/25)

    # implement Bresenham's algo here
    turnMotorByHalfStepping(leftSteps, leftMotorGPIOPins)
    turnMotorByHalfStepping(rightSteps, rightMotorGPIOPins)

turnMotors(10,-20)

x0 = 0
y0 = 290

def move(x1,y1):

    # current pen position :
    global x0, y0

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
    
    x0,y0 = x1,y1 # update current pen position


GPIO.cleanup()
