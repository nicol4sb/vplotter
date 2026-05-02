"""Pure v-plotter frame math (mm). Safe to import without GPIO."""

from __future__ import annotations

import math

HALF_DISTANCE_BETWEEN_MOTORS_MM = 285
PEN_TO_BAR_VERTICAL_DISTANCE_MM = 320

# Plot mm → model mm (tuned: square + 120 mm portrait bbox vs 140×115 mm measured).
CALIB_SCALE_X = 0.476190
CALIB_SCALE_Y = 0.485339


def left_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM + x)


def right_string_length_mm(x: float, y: float) -> float:
    dy = PEN_TO_BAR_VERTICAL_DISTANCE_MM - y
    return math.hypot(dy, HALF_DISTANCE_BETWEEN_MOTORS_MM - x)
