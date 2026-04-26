#!/usr/bin/python3
from __future__ import annotations


def read_file(path: str) -> list[list[float]]:
    out: list[list[float]] = []
    with open(path) as fp:
        for line in fp:
            p = line.split()
            if len(p) < 3 or p[0] != "G03":
                continue
            out.append([float(p[1][1:]), float(p[2][1:])])
    return out
