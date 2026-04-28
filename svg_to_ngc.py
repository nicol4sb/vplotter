#!/usr/bin/python3
from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


CMD_RE = re.compile(r"[MmLlCcZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")


def parse_path_d(path_d: str) -> list[tuple[float, float]]:
    tokens = CMD_RE.findall(path_d)
    i = 0
    cmd = None
    x = y = 0.0
    sx = sy = 0.0
    points: list[tuple[float, float]] = []

    def take_num() -> float:
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    def sample_cubic(
        p0: tuple[float, float],
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
        n: int = 10,
    ) -> list[tuple[float, float]]:
        out = []
        for k in range(1, n + 1):
            t = k / n
            a = (1 - t) ** 3
            b = 3 * (1 - t) ** 2 * t
            c = 3 * (1 - t) * t * t
            d = t**3
            out.append(
                (
                    a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
                )
            )
        return out

    while i < len(tokens):
        if re.fullmatch(r"[MmLlCcZz]", tokens[i]):
            cmd = tokens[i]
            i += 1
        if cmd is None:
            raise ValueError("Invalid SVG path: missing command")

        if cmd in ("M", "m"):
            first = True
            while i < len(tokens) and not re.fullmatch(r"[MmLlCcZz]", tokens[i]):
                nx, ny = take_num(), take_num()
                if cmd == "m":
                    nx += x
                    ny += y
                x, y = nx, ny
                if first:
                    sx, sy = x, y
                    first = False
                points.append((x, y))
            cmd = "L" if cmd == "M" else "l"
        elif cmd in ("L", "l"):
            while i < len(tokens) and not re.fullmatch(r"[MmLlCcZz]", tokens[i]):
                nx, ny = take_num(), take_num()
                if cmd == "l":
                    nx += x
                    ny += y
                x, y = nx, ny
                points.append((x, y))
        elif cmd in ("C", "c"):
            while i < len(tokens) and not re.fullmatch(r"[MmLlCcZz]", tokens[i]):
                x1, y1, x2, y2, x3, y3 = (
                    take_num(),
                    take_num(),
                    take_num(),
                    take_num(),
                    take_num(),
                    take_num(),
                )
                if cmd == "c":
                    p1, p2, p3 = (x + x1, y + y1), (x + x2, y + y2), (x + x3, y + y3)
                else:
                    p1, p2, p3 = (x1, y1), (x2, y2), (x3, y3)
                p0 = (x, y)
                points.extend(sample_cubic(p0, p1, p2, p3, n=10))
                x, y = p3
        elif cmd in ("Z", "z"):
            x, y = sx, sy
            points.append((x, y))

    # remove consecutive duplicates
    clean = [points[0]]
    for p in points[1:]:
        if abs(p[0] - clean[-1][0]) > 1e-9 or abs(p[1] - clean[-1][1]) > 1e-9:
            clean.append(p)
    # avoid explicit duplicate close point in single-stroke output
    if (
        len(clean) > 2
        and abs(clean[0][0] - clean[-1][0]) < 1e-9
        and abs(clean[0][1] - clean[-1][1]) < 1e-9
    ):
        clean = clean[:-1]
    return clean


def choose_start(points: list[tuple[float, float]], mode: str) -> int:
    if mode == "first":
        return 0
    if mode == "left":
        return min(range(len(points)), key=lambda i: points[i][0])
    if mode == "right":
        return max(range(len(points)), key=lambda i: points[i][0])
    if mode == "top":
        return max(range(len(points)), key=lambda i: points[i][1])
    if mode == "bottom":
        return min(range(len(points)), key=lambda i: points[i][1])
    # belly = lowest points, then closest to center x
    ys = [p[1] for p in points]
    min_y, max_y = min(ys), max(ys)
    band = min_y + 0.05 * (max_y - min_y)
    idxs = [i for i, (_, y) in enumerate(points) if y <= band]
    if not idxs:
        return min(range(len(points)), key=lambda i: points[i][1])
    return min(idxs, key=lambda i: abs(points[i][0]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert SVG path to single-stroke G03 NGC.")
    parser.add_argument("--svg", required=True, help="Input SVG path file")
    parser.add_argument("--out", required=True, help="Output .ngc file path")
    parser.add_argument(
        "--path-id",
        default="path50",
        help="SVG path id to use (default: path50)",
    )
    parser.add_argument(
        "--width-mm",
        type=float,
        default=56.0,
        help="Target width in mm (default: 56)",
    )
    parser.add_argument(
        "--start",
        choices=["belly", "first", "left", "right", "top", "bottom"],
        default="belly",
        help="Where to rotate start point (default: belly)",
    )
    args = parser.parse_args()

    svg_path = Path(args.svg)
    out_path = Path(args.out)
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # path tags can be namespaced
    paths = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")
    chosen = None
    for p in paths:
        if p.get("id") == args.path_id:
            chosen = p
            break
    if chosen is None:
        print(f"Path id '{args.path_id}' not found in {svg_path}", file=sys.stderr)
        sys.exit(1)

    d = chosen.get("d")
    if not d:
        print(f"Path '{args.path_id}' has no d attribute", file=sys.stderr)
        sys.exit(1)

    points = parse_path_d(d)
    if not points:
        print("No points parsed from SVG path", file=sys.stderr)
        sys.exit(1)

    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    spanx = maxx - minx
    scale = args.width_mm / spanx if spanx else 1.0
    cx, cy = (minx + maxx) / 2.0, (miny + maxy) / 2.0
    points = [((x - cx) * scale, (y - cy) * scale) for x, y in points]

    start_idx = choose_start(points, args.start)
    points = points[start_idx:] + points[:start_idx]

    lines = [
        "(Generated by svg_to_ngc.py)",
        f"(source={svg_path.name}, path_id={args.path_id})",
        f"(width_mm={args.width_mm:.3f}, start={args.start})",
        "G21",
        "G90",
    ]
    for x, y in points:
        lines.append(f"G03 X{x:.3f} Y{y:.3f}")
    out_path.write_text("\n".join(lines) + "\n")

    x2 = [x for x, _ in points]
    y2 = [y for _, y in points]
    print(f"Wrote {out_path}")
    print(f"points={len(points)}")
    print(
        f"x=[{min(x2):.3f},{max(x2):.3f}] span={max(x2)-min(x2):.3f} | "
        f"y=[{min(y2):.3f},{max(y2):.3f}] span={max(y2)-min(y2):.3f}"
    )


if __name__ == "__main__":
    main()
