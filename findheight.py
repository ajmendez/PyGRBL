#!/usr/bin/env python
####################################
# findheight.py
# calibrates the height using a little bit of the board.
# [2012.02.10] Mendez -- init
####################################


# Start with inches and absolute position
print '''(findheight.py)'
(Lower the bit to just touching the board when it is unpowered.)
(Start with the board at (0,0,0), we will do this in negative y direction.)
G20
G90'''

xbound = [ 0.000,  -0.750] # inch
ybound = [-0.010, -0.010]
zbound = [ 0.000, -0.010] #inch
ntick = 4
ticklen = 0.050 #inch
def findloc(p, bound):
  return bound[0] + p*(bound[1] - bound[0])

def printloc(x,y,z,move=False):
  if move: prefix=0 
  else: prefix = 1
  print 'G%02d X%5.3f Y%5.3f Z%5.3f'%(prefix,x,y,z)

printloc(0,0,0, move=True)
printloc(0,0,zbound[1])
printloc(0,0,ticklen, move=True)
printloc(xbound[0],ybound[0],ticklen, move=True)
printloc(xbound[0],ybound[0],0)
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




