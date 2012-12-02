#!/usr/bin/env python
# circle.py
# [2012.10.27] Mendez written

from lib.util import IndexDict
# import lib.tool 

Z_MOVE =  0.020 # [0.020 in]
Z_MILL = -0.007 # [0.007 in] 

def _circle(x, y, r, depth):
	moves = []
	cmd     = [0,1,2,2,2]
	xOffset = [0,0,0,r,0,-r]
	yOffset = [0,r,r,0,-r,0]
	m = IndexDict()
	m[0],m[1],m[2],m[3] = (x,y,Z_MOVE,0)
	moves.append(m)
	m = IndexDict()
	m[0],m[1],m[2],m[3] = (x+r,y,Z_MOVE,0)
	moves.append(m)
	m = IndexDict()
	m[0],m[1],m[2],m[3] = (x+r,y,Z_MILL,1)
	moves.append(m)

	for xo,yo in zip(xOffset,yOffset):
		m = IndexDict()
		m.x,m.y,m.cmd,m.i,m.j = (x+xo,y+yo,2,-yo,-xo)
		m.updateName()
		moves.append(m)

	for m in moves:
		print m.toGcode()
	




def makeCircle():
	# T = tool.Tool()
	c = _circle(0,0,1,-0.25)


if __name__ == "__main__":
	makeCircle()

