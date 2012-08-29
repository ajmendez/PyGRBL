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
from lib.util import deltaTime
from lib.clint.textui import puts, colored



def main(gfile):
	start = datetime.now()
	name = gfile if isinstance(gfile,str) else gfile.name
	puts(colored.blue('Visualizing the file: %s\n Started: %s'%(name,datetime.now())))

	# Read in the gcode
	gcode = GCode(gfile, limit=None)
	gcode.parse()
	
	# parse the code into an array of tool moves
	tool = Tool(gcode)
	tool.uniq()
	box = tool.boundBox()

	print 'length gcode: %d, length tool: %d'%(len(gcode),len(tool))

	# plot it out
	with Image('fig1.eps', gridsize=box[0:2]) as image:
		image.process(tool)

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
  
