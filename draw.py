#!/usr/bin/env python
# draw.py : simulate mill/drill/etch to an EPS file
# [2015-04-17] - bkurtz
import os, re, sys
from math import ceil
from datetime import datetime
from lib.gcode import GCode
from lib.tool import Tool
from lib.drawing import Drawing
from lib import argv
from lib.util import deltaTime
from clint.textui import puts, colored


def main(etch_file, args=None):
	start = datetime.now()
	name = etch_file if isinstance(etch_file,str) else etch_file.name
	puts(colored.blue('Visualizing the file: %s\n Started: %s'%(name,datetime.now())))

	# Read in the gcode
	gcode = GCode(etch_file, limit=None)
	gcode.parse()
	
	# parse the code into an array of tool moves
	tool = Tool(gcode)
	box = tool.boundBox()
	
	# proces and save image
	outfile = os.path.splitext(etch_file.name)[0] + '.eps'
	print box
	print box[0:2]
	image = Drawing(outfile)#, bbox=box)
	image.process(tool)
	image.save()

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
	                getDevice=False) # We dont need a device


	# optimize each file in the list
	for gfile in args.gcode:
	  # only process things not processed before.
	  # c = re.match(r'(?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap)', gfile.name)
	  c = re.match(r'(.+)(\.tap)', gfile.name)
	  # c = True # HAX and accept everything
	  if c: # either a drill.tap or etch.tap file
	    main(gfile, args=args)

	print '%s finished in %s'%(args.name,deltaTime(start))
  
