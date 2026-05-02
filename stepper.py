#!/usr/bin/python3
# coding=UTF-8
"""
V-plotter: XY targets -> left/right string deltas -> half-stepped 28BYJ-48.

On a Pi, rename/remove the repo's RPi/ stub so `import RPi.GPIO` loads the system module.
"""
from __future__ import annotations

import math
import sys
import time

import RPi.GPIO as GPIO

from geometry import left_string_length_mm, right_string_length_mm
from points_file_reader import read_file

# --- Pins (BOARD numbering) ---
RIGHT_MOTOR_PINS = [15, 13, 11, 7]
LEFT_MOTOR_PINS = [10, 12, 16, 18]

# --- Mechanics ---
HALF_STEP_DELAY_SEC = 0.0007
HALF_STEPS_PER_SHAFT_REV = 4096
PULLEY_PERIMETER_MM = 23.56

# If pure Y moves look horizontal, one spool steps opposite the model: set that side to -1.
LEFT_MOTOR_STRING_SIGN = 1
RIGHT_MOTOR_STRING_SIGN = 1

# NGC/preview coords are multiplied by this before kinematics. Use -1.0 if +X and +Y on the wall
# are opposite the matplotlib preview (both axes “inverted”).
PLOT_XY_SIGN = 1.0

# Pen state (mm, same frame as geometry.py)
x0 = 0.0
y0 = 0.0

HALF_STEP_PHASES = [
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
]

_phase_right = 0
_phase_left = 0


def configure_gpio() -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)


def reset_outputs_low() -> None:
    for group in (LEFT_MOTOR_PINS, RIGHT_MOTOR_PINS):
        for pin in group:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)


def _motor_side(pins: list[int]) -> str:
    return "right" if pins is RIGHT_MOTOR_PINS else "left"


def turn_motor_half_steps(count: int, pins: list[int]) -> None:
    """+count = extend string (per your wiring / phase table)."""
    global _phase_right, _phase_left

    if count == 0:
        return

    if _motor_side(pins) == "right":
        phase = _phase_right
        _phase_right += count
    else:
        phase = _phase_left
        _phase_left += count

    step = 1 if count > 0 else -1
    side = _motor_side(pins)

    for _ in range(abs(count)):
        phase = (phase + 8 + step) % 8
        # print("Motor", side, "phase", phase)  # very chatty: every half-step
        for w in range(4):
            GPIO.output(pins[w], HALF_STEP_PHASES[phase][w])
        time.sleep(HALF_STEP_DELAY_SEC)


def mm_to_half_steps(delta_mm: float) -> int:
    return int(delta_mm * HALF_STEPS_PER_SHAFT_REV / PULLEY_PERIMETER_MM)


def turn_motors(left_mm: float, right_mm: float) -> None:
    """Bresenham-style interleaving so both spools move together in string space."""
    left_mm *= LEFT_MOTOR_STRING_SIGN
    right_mm *= RIGHT_MOTOR_STRING_SIGN
    left_steps = mm_to_half_steps(left_mm)
    right_steps = mm_to_half_steps(right_mm)

    if right_steps == 0:
        turn_motor_half_steps(left_steps, LEFT_MOTOR_PINS)
        return

    slope = abs(left_mm / right_mm)
    rounded = int(slope)
    err = 0.0
    sgn_r = int(math.copysign(1, right_steps))
    sgn_l = int(math.copysign(1, left_steps))

    for _ in range(abs(right_steps)):
        turn_motor_half_steps(sgn_r, RIGHT_MOTOR_PINS)
        turn_motor_half_steps(int(rounded * sgn_l), LEFT_MOTOR_PINS)
        err += slope - rounded
        while err > 1:
            turn_motor_half_steps(sgn_l, LEFT_MOTOR_PINS)
            err -= 1


def move(x1: float, y1: float) -> None:
    global x0, y0

    x1 *= PLOT_XY_SIGN
    y1 *= PLOT_XY_SIGN
    print("Move:", (x0, y0), "->", (x1, y1))
    dL = left_string_length_mm(x1, y1) - left_string_length_mm(x0, y0)
    dR = right_string_length_mm(x1, y1) - right_string_length_mm(x0, y0)
    turn_motors(dL, dR)
    x0, y0 = x1, y1
    print("At:", (x0, y0))


# --- Built-in tests ---
JOG_HALF_STEPS = 10
FULL_REV_HALF_STEPS = HALF_STEPS_PER_SHAFT_REV


def run_motor_jog_test() -> None:
    for pins in (LEFT_MOTOR_PINS, RIGHT_MOTOR_PINS):
        turn_motor_half_steps(+JOG_HALF_STEPS, pins)
        turn_motor_half_steps(-JOG_HALF_STEPS, pins)


def run_full_revolution_test() -> None:
    for pins in (RIGHT_MOTOR_PINS, LEFT_MOTOR_PINS):
        turn_motor_half_steps(FULL_REV_HALF_STEPS, pins)
        turn_motor_half_steps(-FULL_REV_HALF_STEPS, pins)


def _prompt_before_return_home() -> None:
    print(
        "Drawing finished. Remove or lift the pen, then press Enter "
        "to return to (0, 0).",
        flush=True,
    )
    if sys.stdin.isatty():
        input()
    else:
        print("(No TTY — waiting 15 s, then returning home.)", flush=True)
        time.sleep(15)


def run_from_ngc(path: str) -> None:
    for x, y in read_file(path):
        move(x, y)
    _prompt_before_return_home()
    move(0.0, 0.0)


def _usage() -> None:
    prog = sys.argv[0] if sys.argv else "stepper.py"
    print(f"Usage: {prog} [test|rev|file.ngc]\n", file=sys.stderr)


def main() -> None:
    actions = {
        "test": run_motor_jog_test,
        "rev": run_full_revolution_test,
    }
    try:
        reset_outputs_low()
        argv = sys.argv[1:]
        if not argv:
            run_motor_jog_test()
            return
        cmd = argv[0]
        if cmd in ("-h", "--help"):
            _usage()
            return
        action = actions.get(cmd)
        if action is not None:
            action()
            return
        run_from_ngc(cmd)
    finally:
        GPIO.cleanup()


# Legacy names
set_gpio_as_output_and_to_0 = reset_outputs_low
turnMotorByHalfStepping = turn_motor_half_steps
turnMotors = turn_motors
string_delta_mm_to_half_steps = mm_to_half_steps
rightMotorGPIOPins = RIGHT_MOTOR_PINS
leftMotorGPIOPins = LEFT_MOTOR_PINS

configure_gpio()

if __name__ == "__main__":
    main()
