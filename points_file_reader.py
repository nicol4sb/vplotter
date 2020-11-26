#!/usr/bin/python

import fileinput

def read_file():
    filepath = './moto.txt'
    
    with open(filepath) as fp:

        instructions = []

        line = fp.readline()
        while line:
            details = line.split(',')
            if details[0] == "C17":
                instructions.append([int(details[1])-5471,int(details[2])-5707])
            line = fp.readline()
        return instructions
