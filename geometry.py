"""Pure v-plotter frame math (mm). Safe to import without GPIO."""

from __future__ import annotations

import math

HALF_DISTANCE_BETWEEN_MOTORS_MM = 285
PEN_TO_BAR_VERTICAL_DISTANCE_MM = 320

# Plot mm → model mm before string math. Re-tune with calibration_square_100mm.ngc: measure edges (mm),
# then CALIB_SCALE_X = 100 / Lx_mean, CALIB_SCALE_Y = 100 / Ly_mean for 10 cm nominal sides.
# Last measure: horizontal 180 mm, vertical 215 mm → nominal 100 mm commands were ~1.8× / 2.15× too large.
CALIB_SCALE_X = 100.0 / 180.0
CALIB_SCALE_Y = 100.0 / 215.0


def left_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM + x)


def right_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM - x)
