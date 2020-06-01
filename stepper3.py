import RPi.GPIO as GPIO
import time, math

GPIO.setmode(GPIO.BOARD)

ControlPinMotor1 = [7, 11, 13, 15]
ControlPinMotor2 = [8, 10, 12, 16]

for pin in ControlPinMotor1:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

for pin in ControlPinMotor2:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

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

halfSteppinglPhaseAnti = [
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1]
]

def turnMotor(stringLength, rightMotorIfTrueElseLeft):

    # calculate number of steps given 25mm perimeter of pulley = 2048 steps -> 4096 half steps
    numberOfHalfSteps = 4096/25 * abs(stringLength)

    # if motor selected is the right one
    pinsToBeActivated = ControlPinMotor1

    # clock-wise rotation? for right motor - else invert
    stepping = halfSteppinglPhaseAnti if stringLength > 0 else halfSteppinglPhase

    if not rightMotorIfTrueElseLeft:
        pinsToBeActivated = ControlPinMotor2

    # rotate
    for _ in range(int(numberOfHalfSteps/4)):     # divide by 4 because we take 4 steps per loop -
        for halfStep in range(8):
            for pin in range(4):
                GPIO.output(pinsToBeActivated[pin], stepping[halfStep][pin])
            time.sleep(0.0015)


def move(x0, y0, x1,y1):

    # distance between the two motors
    d = 290 #mm

    # turn left motor by ?
    distmg = math.sqrt(y1**2+(d+x1)**2) - math.sqrt(y0**2+(d+x0)**2)
    print("dist moteur gauche", distmg)
    turnMotor(distmg, False)

    # turn right motor by ?
    distmd = math.sqrt(y1**2+(d-x1)**2) - math.sqrt(y0**2+(d-x0)**2)
    print("dist moteur droit", distmd)
    turnMotor(- distmd, True)


# initial position of the pen : 
# x0 = 0  --- on the bissector between the 2 motors
# y0 = 290 --- 290mm down on the bisector of the 2 motors
x0 = 0
y0 = 290

# draw a square - yay ! - size unknown as lines are not straight - but it's a square. 
for _ in range(400):
    x1 = x0
    y1 = y0+0.1
    move(x0,y0,x1,y1)
    x0 = x1
    y0 = y1

for _ in range(400):
    x1 = x0-0.1
    y1 = y0
    move(x0,y0,x1,y1)
    x0 = x1
    y0 = y1

for _ in range(400):
    x1 = x0
    y1 = y0-0.1
    move(x0,y0,x1,y1)
    x0 = x1
    y0 = y1

for _ in range(400):
    x1 = x0+0.1
    y1 = y0
    move(x0,y0,x1,y1)
    x0 = x1
    y0 = y1


GPIO.cleanup()

