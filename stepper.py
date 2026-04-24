#!/usr/bin/python3
# coding=UTF-8
"""
V-plotter: XY targets -> left/right string length deltas -> half-stepped 28BYJ-48 motors.

On a Raspberry Pi, rename or remove the repo's RPi/ stub package so
`import RPi.GPIO` resolves to the system module (apt: python3-rpi.gpio).
"""
from __future__ import annotations

import math
import sys
import time

import RPi.GPIO as GPIO

from points_file_reader import read_file

# --- GPIO (BOARD numbering: physical header pins) ---

RIGHT_MOTOR_PINS = [15, 13, 11, 7]
LEFT_MOTOR_PINS = [10, 12, 16, 18]

# --- Timing / mechanics ---

# Delay after each half-step (coils need time to settle; too low = missed steps).
HALF_STEP_DELAY_SEC = 0.0007

# 28BYJ-48 + gearbox: commonly ~4096 half-steps per output-shaft revolution (approximate).
HALF_STEPS_PER_SHAFT_REV = 4096

# String contact circle on the pulley (~7.5 mm ID -> circumference in mm).
PULLEY_PERIMETER_MM = 23.56

# Print every half-step (very noisy during long moves).
VERBOSE_HALF_STEPS = True

# --- Plotter frame (mm): origin and Y axis per your mechanical layout ---

HALF_DISTANCE_BETWEEN_MOTORS_MM = 285
PEN_TO_BAR_VERTICAL_DISTANCE_MM = 320

# Current pen position (updated by move()).
x0 = 0.0
y0 = 0.0

# --- Half-step sequence (8 phases, 4 wires) ---

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

# Best-effort phase index per motor (0..7); real rotor may differ slightly on power-up.
_right_motor_phase = 0
_left_motor_phase = 0


def configure_gpio() -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)


configure_gpio()


def reset_outputs_low() -> None:
    for pin_group in (LEFT_MOTOR_PINS, RIGHT_MOTOR_PINS):
        for pin in pin_group:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)


def _is_right_motor(pins: list[int]) -> bool:
    return pins is RIGHT_MOTOR_PINS


def turn_motor_half_steps(count: int, pins: list[int]) -> None:
    """Step one motor by `count` half-steps (+ extends string per your wiring / phase table)."""
    global _right_motor_phase, _left_motor_phase

    if count == 0:
        return

    if _is_right_motor(pins):
        phase = _right_motor_phase
        _right_motor_phase += count
    else:
        phase = _left_motor_phase
        _left_motor_phase += count

    step = 1 if count > 0 else -1
    label = "right" if _is_right_motor(pins) else "left"

    for _ in range(abs(count)):
        phase = (phase + 8 + step) % 8
        if VERBOSE_HALF_STEPS:
            print("Motor", label, "phase", phase)
        for wire in range(4):
            GPIO.output(pins[wire], HALF_STEP_PHASES[phase][wire])
        time.sleep(HALF_STEP_DELAY_SEC)


def string_delta_mm_to_half_steps(delta_mm: float) -> int:
    return int(delta_mm * HALF_STEPS_PER_SHAFT_REV / PULLEY_PERIMETER_MM)


def turn_motors(left_mm: float, right_mm: float) -> None:
    """
    Interleave left/right half-steps (Bresenham-style) so both spools move together
    for diagonal-ish motion in string space.
    """
    left_steps = string_delta_mm_to_half_steps(left_mm)
    right_steps = string_delta_mm_to_half_steps(right_mm)

    if right_steps == 0:
        turn_motor_half_steps(left_steps, LEFT_MOTOR_PINS)
        return

    slope = abs(left_mm / right_mm)
    rounded = int(slope)
    deviation = 0.0

    for _ in range(abs(right_steps)):
        turn_motor_half_steps(int(math.copysign(1, right_steps)), RIGHT_MOTOR_PINS)
        turn_motor_half_steps(int(rounded * math.copysign(1, left_steps)), LEFT_MOTOR_PINS)
        deviation += slope - rounded
        while deviation > 1:
            turn_motor_half_steps(int(math.copysign(1, left_steps)), LEFT_MOTOR_PINS)
            deviation -= 1


def _left_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM + x)


def _right_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM - x)


def move(x1: float, y1: float) -> None:
    global x0, y0

    print("going from", x0, y0, "to", x1, y1)

    d_left = _left_string_length_mm(x1, y1) - _left_string_length_mm(x0, y0)
    d_right = _right_string_length_mm(x1, y1) - _right_string_length_mm(x0, y0)

    turn_motors(d_left, d_right)
    x0, y0 = x1, y1
    print("Head now positioned at", x0, y0)


# --- Built-in tests ---

JOG_HALF_STEPS = 10
FULL_REV_HALF_STEPS = HALF_STEPS_PER_SHAFT_REV


def run_motor_jog_test() -> None:
    """Short back-and-forth jog on each motor."""
    turn_motor_half_steps(+JOG_HALF_STEPS, LEFT_MOTOR_PINS)
    turn_motor_half_steps(-JOG_HALF_STEPS, LEFT_MOTOR_PINS)
    turn_motor_half_steps(+JOG_HALF_STEPS, RIGHT_MOTOR_PINS)
    turn_motor_half_steps(-JOG_HALF_STEPS, RIGHT_MOTOR_PINS)


def run_full_revolution_test() -> None:
    """One shaft revolution each motor forward then back (sanity / mechanical check)."""
    turn_motor_half_steps(FULL_REV_HALF_STEPS, RIGHT_MOTOR_PINS)
    turn_motor_half_steps(-FULL_REV_HALF_STEPS, RIGHT_MOTOR_PINS)
    turn_motor_half_steps(FULL_REV_HALF_STEPS, LEFT_MOTOR_PINS)
    turn_motor_half_steps(-FULL_REV_HALF_STEPS, LEFT_MOTOR_PINS)


def run_from_ngc(path: str) -> None:
    for xy in read_file(path):
        move(xy[0], xy[1])


def _print_usage() -> None:
    prog = sys.argv[0] if sys.argv else "stepper.py"
    print(
        f"Usage:\n"
        f"  {prog}              # jog test\n"
        f"  {prog} test         # jog test\n"
        f"  {prog} rev          # full revolution + reverse, each motor\n"
        f"  {prog} file.ngc     # run G03 points from file\n",
        file=sys.stderr,
    )


def main() -> None:
    configure_gpio()
    try:
        reset_outputs_low()
        if len(sys.argv) >= 2:
            arg = sys.argv[1]
            if arg in ("-h", "--help"):
                _print_usage()
                return
            if arg == "test":
                run_motor_jog_test()
            elif arg == "rev":
                run_full_revolution_test()
            else:
                run_from_ngc(arg)
        else:
            run_motor_jog_test()
    finally:
        GPIO.cleanup()


# Backwards-compatible names for interactive / one-off scripts
set_gpio_as_output_and_to_0 = reset_outputs_low
turnMotorByHalfStepping = turn_motor_half_steps
turnMotors = turn_motors
rightMotorGPIOPins = RIGHT_MOTOR_PINS
leftMotorGPIOPins = LEFT_MOTOR_PINS

if __name__ == "__main__":
    main()
