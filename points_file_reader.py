#!/usr/bin/python

import fileinput

def read_file(file_name):
    
    with open(file_name) as fp:

        instructions = []

        line = fp.readline()
        while line:
            details = line.split(' ')
            if details[0] == "G03":
                instructions.append([float(details[1][1:]),float(details[2][1:])])
            line = fp.readline()
        return instructions
