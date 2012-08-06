#!/usr/bin/env python
# findheight.py: Prints out a calibration program for z_height.
# [2012.02.10] Mendez -- init


# Start with inches and absolute position
HEADER = '''\
(findheight.py)'
(Lower the bit to just touching the board when it is unpowered.)
(Start with the board at x=0,y=0,z=0)
G20 (inch)
G90 (absolute)'''

# Motion limits:
xbound = [ 0.000, -0.750] # inch : absolute position of start/end of depthcut
ybound = [-0.010, -0.010] # inch : absolute position of y line
zbound = [ 0.000, -0.010] # inch : start/end height of mill depth
ntick = 4                 # Num  : Number of ticks
ticklen = 0.050           # inch : length of ticks and move height

# Mill linearly from zbound[0] to zbound[1]
# +---  [starts at xbound[0],ybound[0]]
# |     
# |     [length of tick lines is given by ybound[0]-ticklen]
# +---  [number of lines depend on ntick]
# |     [Vert length is given by xbound delta]
# |     
# +---  
# |     
# |     
# +---  [end position xbound[1],ybound[0]-ticklen]
#                   [! After mill moves back to origin]


# some basic funcions
def findloc(p, bound):
  '''from a fraction p, and the bounds return the location we should be.'''
  return bound[0] + p*(bound[1] - bound[0])

def printloc(x,y,z,move=False):
  '''given X, Y, Z coordinates, print out a move/mill gcode'''
  prefix = 0 if move else 1
  print 'G%02d X%5.3f Y%5.3f Z%5.3f'%(prefix,x,y,z)



# Prints to stdout
print HEADER
printloc(0,0,0, move=True) # start at origin
printloc(0,0,zbound[1]) # mill a hole at origin
printloc(0,0,ticklen, move=True) # raise by ticklen
printloc(xbound[0],ybound[0],ticklen, move=True) # go to start position
printloc(xbound[0],ybound[0],zbound[0])


for i in range(ntick):
  p = i/float(ntick-1)
  x = findloc(p, xbound)
  y = findloc(p, ybound)
  z = findloc(p, zbound)
  printloc(x,y,z)
  printloc(x,y-ticklen,z)
  printloc(x,y,z)

printloc(x,y,ticklen, move=True)
printloc(0,0,ticklen, move=True)
printloc(0,0,0, move=True)




