#!/usr/bin/python3
"""
Live 2D preview of the pen path from an NGC file (same G03 points as stepper.py).

Uses matplotlib; no GPIO. Tune --delay to watch the path draw segment by segment.

  python3 preview_ngc.py picasso_0005.ngc --delay 0.02
"""
from __future__ import annotations

import argparse
import sys
import time

from points_file_reader import read_file


def _prompt_before_return_home() -> None:
    print(
        "Preview: path done. Press Enter to animate return to (0, 0).",
        flush=True,
    )
    if sys.stdin.isatty():
        input()
    else:
        time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Animated NGC pen path preview (mm).")
    parser.add_argument("ngc", help="Path to .ngc file (G03 X… Y… lines)")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.05,
        metavar="SEC",
        help="Pause after each segment (default: 0.05)",
    )
    parser.add_argument(
        "--hold",
        type=float,
        default=0.0,
        metavar="SEC",
        help="Extra time to leave the window open at the end (default: 0 = until closed)",
    )
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "matplotlib is required: python3 -m pip install matplotlib",
            file=sys.stderr,
        )
        sys.exit(1)

    points = read_file(args.ngc)
    if not points:
        print("No G03 points found.", file=sys.stderr)
        sys.exit(1)

    all_x = [0.0] + [p[0] for p in points]
    all_y = [0.0] + [p[1] for p in points]
    margin = max(5.0, 0.05 * (max(all_x) - min(all_x) or 1))
    margin_y = max(5.0, 0.05 * (max(all_y) - min(all_y) or 1))

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(args.ngc)
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)

    (path_line,) = ax.plot([0.0], [0.0], color="tab:blue", linewidth=0.9, label="path")
    ax.scatter([0.0], [0.0], s=12, c="green", zorder=5, label="start")
    ax.legend(loc="upper right", fontsize=8)

    plt.ion()
    plt.show()

    xs: list[float] = [0.0]
    ys: list[float] = [0.0]

    for x1, y1 in points:
        xs.append(x1)
        ys.append(y1)
        path_line.set_data(xs, ys)
        ax.scatter([x1], [y1], s=4, c="black", alpha=0.35, zorder=4)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(args.delay)

    _prompt_before_return_home()

    # Back to origin (matches stepper.run_from_ngc)
    xs.append(0.0)
    ys.append(0.0)
    path_line.set_data(xs, ys)
    ax.scatter([0.0], [0.0], s=8, c="green", alpha=0.9, zorder=5)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(args.delay)

    plt.ioff()
    if args.hold > 0:
        plt.pause(args.hold)
    plt.show(block=True)


if __name__ == "__main__":
    main()
