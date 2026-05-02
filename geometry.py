"""Pure v-plotter frame math (mm). Safe to import without GPIO."""

from __future__ import annotations

import math

HALF_DISTANCE_BETWEEN_MOTORS_MM = 285
PEN_TO_BAR_VERTICAL_DISTANCE_MM = 320

# Plot mm → model mm before string math. Draw calibration_square_100mm.ngc, measure horizontal vs
# vertical edge lengths (mm). Set CALIB_SCALE_X = 100 / Lx_mean, CALIB_SCALE_Y = 100 / Ly_mean.
CALIB_SCALE_X = 1.0
CALIB_SCALE_Y = 1.0


def left_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM + x)


def right_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM - x)
