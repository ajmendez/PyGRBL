#!/usr/bin/env python
# visualize.py : A set of nice modifications for gcode
# [2012.08.21] - Mendez 
import os, re
# from datetime import datetime
from lib.image import Image
from lib.gcode import GCode
from lib.tool import Tool
# from lib import argv
# from lib.util import deltaTime
# from lib.clint.textui import puts,colored

gfile = os.path.expanduser('~/Dropbox/Shared/robottown/pcb_design/doubleSided/Mendez.bot.etch.tap')
gfile = os.path.expanduser('~/Downloads/Alexander.txt')
gfile='~/Dropbox/Shared/robottown/pcb_design/encoderMotor/controller.bot.etch_opt.tap'
gfile = '~/Dropbox/Shared/robottown/pcb_design/encoderMotor/controller.bot.etch_alex_new.tap'
# with Image('test.ps') as image:

#
def update_path(x,y):
	tmp = [x+offset[0],y+offset[1]]
	if len(path) < 1 or tmp != path[-1]:
		path.append(tmp)

with Image('~/tmp/test.ps') as image:
	gcode = GCode(gfile)
	gcode.parse()
	tool = Tool(gcode)
	tool.uniq()
	box = tool.boundBox()

	path = []
	offset = [-box[0][0],-box[1][0]]
	# for i,[x,y,z,t] in enumerate(tool):
	# 	path.append([x+offset[0],y+offset[1]])
	# 	# print i,t, path[-1]
	# x,y = zip(*path)
	# image.move(x,y)



	last_t = 0 # starts with a move
	path = []
	for i,[x,y,z,t] in enumerate(tool):
		# print i, x,y, t, last_t, path
		if t == last_t:
			update_path(x,y)
		else:
			xarr,yarr = zip(*path)
			print len(path)
			if len(path) == 1:
				image.drill(xarr[0],yarr[0])
			elif t == 1:
				image.mill(xarr,yarr)
			else:
				image.move(xarr,yarr)
			path = []
			update_path(x,y)
			last_t = t


  # print image.filename







# def main(gfile):
#   start = datetime.now()
#   puts(colored.blue('Modifying file: %s\n Started: %s'%(gfile.name,datetime.now())))
#   
#   
#   
#   # how long did this take?
#   puts(colored.green('Time to completion: %s'%(deltaTime(start))))
#   print
# 
# 
# 
# ## I should wrap this in a __main__ section
# # Initialize the args
# start = datetime.now()
# args = argv.arg(description='PyGRBL gcode imaging tool',
#                 getFile=True, # get gcode to process
#                 getMultiFiles=True, # accept any number of files
#                 # otherOptions=otherOptions, # Install some nice things
#                 getDevice=False) # We dont need a device
# 
# 
# # optimize each file in the list
# for gfile in args.gcode:
#   # only process things not processed before.
#   # c = re.match(r'(?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap)', gfile.name)
#   c = re.match(r'(.+)(\.tap)', gfile.name)
#   if c: # either a drill.tap or etch.tap file
#     main(gfile)
# 
# print '%s finished in %s'%(args.name,deltaTime(start))
  
