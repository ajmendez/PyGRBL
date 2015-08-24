#!/usr/bin/env python
# optimize.py : Optimizes a set of paths from a pcbGcode.
# [2011.12.25] Mendez written
# [2012.07.31] Mendez cleaned up handles drills
import sys, getopt, os, re
from datetime import datetime
from lib import argv
from lib.util import deltaTime
from lib.gcode import GCode
from lib.tool import Tool
from clint.textui import colored, puts, indent, progress

FILEENDING = '_opt' # file ending for optimized file.
Z_MOVE  =   20 # mil  [20] : Height above board for a move
Z_MILL  =   -7 # mil  [-7] : Mill depth into board for traces
Z_SPOT  =   -9 # mil  [-9] : Mill depth for spot drill holes
Z_DRILL =  -63 # mil [-63] : Mill depth for full drill holes


# The Optimize function
def opt(gfile, offset=(0.0,0.0,0.0), rotate=False, isDrill=False):
  '''Optimization core function:
  Reads in gCode ascii file.
  Processes gcode into toolpath list
  figures out milling.
  Reorders milling to get optimal
  Writes out to new file.'''
  
  start = datetime.now()
  puts(colored.blue('Optimizing file: %s\n Started: %s'%(gfile.name,datetime.now())))
  
  # Parse the gcode from the ascii to a list of command numbers and location
  gcode = GCode(gfile)
  gcode.parse()
  
  # Take the list and make a toolpath out of it. A toolpath is a list of locations
  # where the bit needs to be moved / milled : [ [x,y,z,t], ...]
  tool = Tool(gcode)
  tool.offset(offset)
  tool.rotate(rotate)
  
  tool.groupMills()
  puts(colored.blue('Toolpath length: %.2f inches, (mill only: %.2f)'%(tool.length(),tool.millLength())))
  if args.setMillHeight:
    tool.setMillHeight(Z_MILL,(Z_DRILL if isDrill else Z_SPOT))
  tool.uniqMills()
  
  # This starts the optimization process:
  # start at here, and go to the next path which is closest is the overall plan
  puts(colored.blue('Starting Optimization:'))
  here = [0.0]*3 # start at the origin
  newMills = []  # accumulate mills here
  k = 0
  while len(tool.mills) > 0:
    # No Optimization
    # mill = tool.mills.pop(0)

    # Basic optimization, find the next closest one and use it.
    # mill = tool.getNextMill(here)

    # Advanced Optimization:  Assumes that each mill path closed, so finds 
    #  the mill path which is close to the point and reorders it to be so
    mill = tool.getClosestMill(here)
    
    # you were here, now you are there
    # move mills and update location
    newMills.append(mill) 
    here = newMills[-1][-1]
    
    k += 1
    if (k%10) == 0:
      sys.stdout.write('.')
      sys.stdout.flush()
    
  tool.mills.extend(newMills)
  tool.reTool(Z_MOVE)
  tool.uniq()
  puts(colored.blue('Toolpath length: %.2f inches, (mill only: %.2f)'%(tool.length(),tool.millLength())))

  # Save this with the _opt file ending.
  output = tool.buildGcode()
  outfile = FILEENDING.join(os.path.splitext(gfile.name))
  puts(colored.green('Writing: %s'%outfile))
  with open(outfile,'w') as f:
    f.write(output)
  
  # how long did this take?
  puts(colored.green('Time to completion: %s'%(deltaTime(start))))
  print



# sometimes we want to keep the mill height
EXTRAARGS = dict(ext=dict(args=['--keepMillHeight'],
                          default=True,
                          const=False,
                          action='store_const',
                          dest='setMillHeight',
                          help='''Do not modify the mill height for 3d mills'''),
                 ext1 = dict(args=['--zmove'],
                          default=0.0, type=float,
                          help='Move Z-height in mills [%s mills]'%Z_MOVE),
                 ext1a = dict(args=['--zmill'],
                          default=0.0, type=float,
                          help='Mill Z-height in mills [%s mills]'%Z_MILL),
                 ext1b = dict(args=['--zdrill'],
                          default=0.0, type=float,
                          help='Drill Z-height in mills [%s mills]'%Z_DRILL),
                
                 ext2=dict(args=['--offsetx'],
                           default=0,
                           type=float,
                           help='Set x offset length in inches'),
                 ext3=dict(args=['--offsety'],
                           default=0.0, type=float,
                           help='Set y offset length in inches'),
                 ext4=dict(args=['--offsetz'],
                           default=0.0, type=float,
                           help='Set z offset length in inches'),
                ext5=dict(args=['--rotate'],
                          default=0.0, type=float,
                          help='Rotate about the origin by some angle. Rotates after offset'),
                )



if __name__ == '__main__':
  # Initialize the args
  start = datetime.now()
  args = argv.arg(description='Python GCode optimizations',
                  otherOptions=EXTRAARGS, # Install some nice things
                  getFile=True, # get gcode to process
                  getMultiFiles=True, # accept any number of files
                  getDevice=False)
  
  if args.zmove != 0:
      Z_MOVE = args.zmove
  if args.zdrill != 0:
      Z_DRILL = args.zdrill
  if args.zmill != 0:
      Z_MILL = args.zmill
  # print vars(args)
  # import sys
  # sys.exit()

  # optimize each file in the list
  for gfile in args.gcode:
    # only process things not processed before.
    # c = re.match(r'(?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap)', gfile.name)
    c = re.match(r'(.+)((?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap))', gfile.name)
    if c: # either a drill.tap or etch.tap file
      opt(gfile, offset=(args.offsetx, args.offsety, args.offsetz), rotate=args.rotate, isDrill=(c.group('drill') > 0))

  print '%s finished in %s'%(args.name,deltaTime(start))


