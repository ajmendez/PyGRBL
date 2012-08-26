#!/usr/bin/env python
# visualize.py : A set of nice modifications for gcode
# [2012.08.21] - Mendez 
import os, re, sys
from math import ceil
from datetime import datetime
from lib.image import Image
from lib.gcode import GCode
from lib.tool import Tool
from lib import argv
from lib.util import deltaTime, distance, memorize
from lib.clint.textui import puts,colored, progress




def update_path(path, x,y,t):
	tmp = [x,y]#[x+offset[0],y+offset[1]]
	if ( (len(path) < 1) or                   # Nothing in path
         ( tmp != path[-1] and                # check that it is uniq 
           ( distance(tmp,path[-1]) < 2 or   # clean out crazy jump
             t != 1 )                      #  but only for mi
          )
        ):
		path.append(tmp)

# @memorize
def getGcode(gfile):
	# parse the gcode into cmds and values
  	gcode = GCode(gfile, limit=None)
	gcode.parse()
	
	# parse the code into an array of tool moves
	tool = Tool(gcode)
	tool.uniq()
	tool._badclean()  # found a bug in a file HAX
	return (tool, gcode)


def main(gfile):
	start = datetime.now()
	name = gfile if isinstance(gfile,str) else gfile.name
	puts(colored.blue('Visualizing the file: %s\n Started: %s'%(name,datetime.now())))
	tool, gcode = getGcode(gfile)
	box = tool.boundBox()
	
	# Build the file
	with Image('fig1.eps', gridsize=box[0:2]) as image:
		last_t = 0 # starts with a move
		path = []
		puts(colored.blue('Drawing paths:'))
		for i,[x,y,z,t] in enumerate(progress.bar(tool)):
			# print 
			# print i, x,y,z,t, len(tool)			
			if t == last_t:
				update_path(path, x,y,t)
			else:
				xarr,yarr = zip(*path)
				if len(path) == 1:
					image.drill(xarr[0],yarr[0])
				elif t == 1:
					image.mill(xarr,yarr)
				else:
					image.move(xarr,yarr)
				path = []
				update_path(path, x,y,t) # there is a point in the stack, add it.
				last_t = t

	# how long did this take?
  	puts(colored.green('Time to completion: %s'%(deltaTime(start))))
  	print


if __name__ == '__main__':
	## I should wrap this in a __main__ section
	# Initialize the args
	start = datetime.now()
	args = argv.arg(description='PyGRBL gcode imaging tool',
	                getFile=True, # get gcode to process
	                getMultiFiles=True, # accept any number of files
	                # otherOptions=otherOptions, # Install some nice things
	                getDevice=False) # We dont need a device


	# optimize each file in the list
	for gfile in args.gcode:
	  # only process things not processed before.
	  # c = re.match(r'(?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap)', gfile.name)
	  c = re.match(r'(.+)(\.tap)', gfile.name)
	  c = True # HAX and accept everything
	  if c: # either a drill.tap or etch.tap file
	    main(gfile)

	print '%s finished in %s'%(args.name,deltaTime(start))
  
