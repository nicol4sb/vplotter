#!/usr/bin/python3


def read_file(file_name):
    instructions = []
    with open(file_name) as fp:
        for line in fp:
            parts = line.split()
            if len(parts) < 3 or parts[0] != "G03":
                continue
            instructions.append([float(parts[1][1:]), float(parts[2][1:])])
    return instructions
