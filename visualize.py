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


FILEENDING ='' # keep it clean going to change file ending anyways

EXTRAARGS = dict(ext=dict(args=['-e','--eps'],
                          default='.pdf',
                          const='.eps',
                          action='store_const',
                          dest='ext',
                          help='''Specify for outputing an eps file rather than a pdf.''') )


def main(gfile, args=None):
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
	
	# proces and save image
	ext = args.ext if args is not None else '.pdf'
	outfile = os.path.splitext(gfile.name)[0] + FILEENDING + ext
	print box
	print box[0:2]
	image = Image(outfile, gridsize=box[0:2])
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
	                otherOptions=EXTRAARGS, # Install some nice things
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
  
