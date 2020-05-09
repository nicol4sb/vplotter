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

steppingDualPhase = [
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
    [1, 0, 0, 1]
]

steppingDualPhaseAnti = [
    [0, 0, 1, 1],
    [0, 1, 1, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 1, 1, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 1]
]


def moveUpOrDown(numberOfTurns, upOrDown):
    for _ in range(numberOfTurns):
        # UP - both motors
        for _ in range(128):
            for step in range(8):
                for pin in range(4):
                    if upOrDown:
                        GPIO.output(
                            ControlPinMotor1[pin], steppingDualPhaseAnti[step][pin])
                        GPIO.output(
                            ControlPinMotor2[pin], steppingDualPhase[step][pin])
                    else:
                        GPIO.output(
                            ControlPinMotor1[pin], steppingDualPhase[step][pin])
                        GPIO.output(
                            ControlPinMotor2[pin], steppingDualPhaseAnti[step][pin])
                time.sleep(0.0015)


def turnMotor(stringLength, rightMotorIfTrueElseLeft):

    # calculate number of steps given 25mm perimeter of pulley = 2048 steps
    numberOfSteps = 2048/25 * abs(stringLength)

    # if motor selected is the right one
    pinsToBeActivated = ControlPinMotor1
    # clock-wise rotation? for right motor - else invert
    stepping = steppingDualPhaseAnti if stringLength > 0 else steppingDualPhase

    if not rightMotorIfTrueElseLeft:
        pinsToBeActivated = ControlPinMotor2

    # rotate
    for _ in range(int(numberOfSteps/8)):     # divide by 8 because we take 8 steps per loop -
        for step in range(8):
            for pin in range(4):
                GPIO.output(pinsToBeActivated[pin], stepping[step][pin])
            time.sleep(0.0015)


x0=0
y0=300

def move(x1,y1):

    global x0
    global y0

    # distance between the two motors
    d = 290

    # turn left motor by ?
    distmg = math.sqrt(y1**2+(d+x1)**2) - math.sqrt(y0**2+(d+x0)**2)
    print("dist moteur gauche", distmg)
    turnMotor(distmg, False)

    # turn right motor by ?
    distmd = math.sqrt(y1**2+(d-x1)**2) - math.sqrt(y0**2+(d-x0)**2)
    print("dist moteur droit", distmd)
    turnMotor(- distmd, True)

    x0 = x1
    y0 = y1


# initialize variables
x0 = 0
y0 = 300

# draw a square - yay ! - size unknown as lines are not straight - but it's a square. 
for _ in range(200):
    move(x0,y0+0.2)

for _ in range(200):
    move(x0-0.2,y0)

for _ in range(200):
    move(x0,y0-0.2)

for _ in range(200):
    move(x0+0.2,y0)

GPIO.cleanup()
