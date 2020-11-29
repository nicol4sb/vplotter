#!/usr/bin/python

import fileinput

def read_file(file_name):
    
    with open(file_name) as fp:

        instructions = []

        line = fp.readline()
        while line:
            details = line.split(',')
            if details[0] == "C17":
                instructions.append([int(details[1]),int(details[2])])
            line = fp.readline()
        return instructions
