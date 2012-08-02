#!/usr/bin/env python
# optimize.py : Optimizes a set of paths from a pcbGcode.
# [2011.12.25] Mendez written
# [2012.07.31] Mendez cleaned up handles drills
import sys, getopt, os
from datetime import datetime
from pprint import pprint

import args
from gcode import GCode
from tool import Tool
from clint.textui import colored, puts, indent, progress

Z_MOVE  =   20 # mil  [20] : Height above board for a move
Z_MILL  =   -7 # mil  [-7] : Mill depth into board for traces
Z_SPOT  =   -9 # mil  [-9] : Mill depth for spot drill holes
Z_DRILL =  -63 # mil [-63] : Mill depth for full drill holes

# Initialize the args
args = args.arg(description='Python GCode optimizations', getFile=True, getDevice=False)

start = datetime.now()
puts(colored.blue('Optimizing file: %s\n Started: %s'%(args.gcode.name,datetime.now())))


# Parse the gcode from the ascii to a list of command numbers and location
gcode = GCode(args.gcode.name)
gcode.parse()


# Take the list and make a toolpath out of it.
tool = Tool(gcode)
tool.groupMills()
# for m in tool.mills: print id(m)
tool.setMillHeight(Z_MILL,Z_SPOT)
tool.uniqMills()

print 'Toolpath length: %.2f inches, (mill only: %.2f)'%(tool.length(),tool.millLength())
# for m in tool.mills:
#   print m
#   for x in m:
#     print '    ',x

while len(tool.mills) > 20: tool.mills.pop()
      

# This starts the optimization process:
# start at here, and go to the next path which is closest is the overall plan
puts(colored.blue('Starting Optimization:'))
here = [0.0]*3
newMills = []
while len(tool.mills) > 0:
  # No Optimization
  # mill = tool.mills.pop(0)
  
  # Basic optimization, find the next closest one and use it.
  # mill = tool.getNextMill(here)
  
  # Advanced Optimization:  Assumes that each mill path closed, so finds 
  #  the mill path which is close to the point and reorders it to be so
  mill = tool.getClosestMill(here)
  
  # you were here, and now update to the end of the mill
  newMills.append(mill)
  here = newMills[-1][-1]
tool.mills.extend(newMills)

tool.reTool(Z_MOVE)
tool.uniq()
print 'Toolpath length: %.2f inches, (mill only: %.2f)'%(tool.length(),tool.millLength())



output = tool.buildGcode()

outfile = '_new'.join(os.path.splitext(args.gcode.name))
puts(colored.green('Writing: %s'%outfile))
with open(outfile,'w') as f:
  f.write(output)
# print output

# for m in tool.mills:
#   print m
  # for x in m:
  #   print '    ',x

sys.exit(1)
