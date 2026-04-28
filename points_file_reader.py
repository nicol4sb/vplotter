#!/usr/bin/python3
from __future__ import annotations


def read_file(path: str) -> list[list[float]]:
    out: list[list[float]] = []
    with open(path) as fp:
        for line in fp:
            p = line.split()
            if not p:
                continue

            # Accept common motion commands that carry XY coordinates.
            # This keeps compatibility with older G03-only files and newer G0/G1 traces.
            if p[0] not in {"G0", "G00", "G1", "G01", "G03"}:
                continue

            x = y = None
            for tok in p:
                if tok.startswith("X"):
                    x = float(tok[1:])
                elif tok.startswith("Y"):
                    y = float(tok[1:])

            if x is None or y is None:
                continue

            out.append([x, y])
    return out
