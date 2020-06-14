VPlotter project. This is a raspberry pi + stepper motors driven vplotter, with the simplest setup I could design. 
Motors had to be 5V so they can be fed with a USB battery along the cards adnand pi.
Code is not specific to any setup and can be parametrized based on your setup.
Be it with other motors, cards, GPIO pins.
Essential concepts are transformation of the rotation of the engines into xy coordinates and Bresenham's algorithm to draw lines somewhat straight between points.
Next on the list :
Draw a line from a set of manually entered points
Build the toolchain to transform a picture to a line of points understandable by the python code.	
