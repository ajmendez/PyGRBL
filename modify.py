#!/usr/bin/env python
# modify.py : A set of nice modifications for gcode
# 2012.08.18 - Mendez
import re, os
from datetime import datetime
from lib import argv
from lib.gcode import GCode
from lib.tool import Tool
from lib.util import deltaTime, error, convertUnits
from clint.textui import puts,colored
# HELLO WORLD
#THESE FILES ARE NOT THE SAME!

FILEENDING = '_mod' # file ending for optimized file.

# We need some specalized arguments for this file, so lets create them here.
OPTIONS = [
  dict(args=['-m', '--move'],
       default=None,
       type=str,
       nargs=1,
       help='''Move the origin to a new point.
               Applied before rotation.
               Specify Units at the end of the x,y pos.
               Example: "-m 0.1,0.2in".'''),
  dict(args=['-r', '--rotate'],
       default=None,
       type=float,
       help='''Rotate the gcode about the origin.
               Applied after a Move.
               In float degrees.'''),
  dict(args=['-c', '--copy'],
       default=None,
       type=str,
       nargs='+',
       help='''Copy the part from the origin to points.
               Applied before rotation.
               Specify Units after each set.
               Example: "-c 0.2,0.2in 20,20mil".'''),
  dict(args=['-x','--replicate'],
       default=None,
       type=str,
       nargs=1,
       help='''Replicate the design by N_x X N_y items.
               Applied before rotation.
               Example: "-x 2,2" ''')
]

#this is a very different parse from the gcode class parse
#it is for parsing user modifications
def parse(move, getUnits=False, defaultUnit='in'):
  '''For Move, Copy, and Replicate, This function evaluates the user input, grabs
  any x,y values and if getUnits is passed gets the units.  Parses any x,y, and
  converts the units to inches, and then outputs an array of the locations to
  move, copy or whatever.  You can use this with an int input (replicate), but
  make sure to cast it to an int.'''
  if isinstance(move, str):
    move = [move]
  #does [no unit specified] need escape chars \[  \]?
  units = r'(?P<units>in|mil|mm|[NoUnitSpecified]?)' if getUnits else r''
  out = []
  for m in move:
    m = re.sub(r'\s','',m).strip()
    g = re.match(r'(?P<x>-?\d*\.?\d*)\,(?P<y>-?\d*\.?\d*)'+units, m, re.I)
    if not g:
      error('Argument Parse Failed on [%s] failed! Check the arguments'%(m))

    # default to inches or a specific unit
    if (g.group('units') is None) or (len(g.group('units')) == 0):
      unit = defaultUnit
    else:
      unit = g.group('units')

    # Ok prepare them for output
    item = map(float,map(g.group,['x','y']))
    if getUnits: item = map(convertUnits,item,[unit]*2)
    if getUnits: item = [convertUnits(x,y) for x,y in zip(item,[unit]*2)]
    out.append(item)
  #
  return (out[0] if len(out) == 1 else out)



def mod(gfile):
  '''For each of the files to process either rotate, move, copy, or
  replicate the code.  General idea:
    read in ascii
    Process into a toolpath list.
    modify.
    Write out toolpath.'''

  start = datetime.now()
  puts(colored.blue('Modifying file: %s\n Started: %s'%(gfile.name,datetime.now())))

  # Parse the gcode.
  gcode = GCode(gfile)
  gcode.parseAll()

  # Create a toolpath from the gcode
  # add in the index so that we can match it to the gcode


  out = []
  if args.move:
    loc = parse(args.move, getUnits=True) # only one move at a time.
    puts(colored.blue('Moving!\n    (0,0) -> (%.3f,%.3f)'%(loc[0],loc[1])))
    tool = Tool()
    tool.build(gcode, addIndex=True)
    tool.move(loc) # ok well this should work
    gcode.update(tool)
    out.append([loc,gcode])

  if args.copy:
    locs = parse(args.copy, getUnits=True)
    puts(colored.blue('Copying!'))
    for loc in locs:
      puts(colored.blue('    (0,0) -> (%.3f,%.3f)'%(loc[0],loc[1])))
      gc = gcode.copy()
      tool = Tool()
      tool.build(gc, addIndex=True)
      tool.move(loc)
      gc.update(tool)
      out.append([loc,gc])

  # if args.replicate:
  #   nxy = map(int,parse(args.replicate)[0]) # ensure int, and only one
  #   puts(colored.blue('Replicating!\n     nx=%i, ny=%i)'%(nxy[0],nxy[1])))

  output = ''.join([o.getGcode(tag=args.name,start=l) for l,o in out])

  outfile = FILEENDING.join(os.path.splitext(gfile.name))
  puts(colored.green('Writing: %s'%outfile))
  with open(outfile,'w') as f:
    f.write(output)

  # how long did this take?
  puts(colored.green('Time to completion: %s'%(deltaTime(start))))
  print




if __name__ == '__main__':
  print parse('0.2,0.3in', getUnits=True)
  print parse('0.2,0.3in', getUnits=True)
  print parse('.2,0.3in', getUnits=True)
  print parse('2,.03mm', getUnits=True)
  print parse('2,3mm', getUnits=True)
  print parse('2222,322mm', getUnits=True)
  print parse('2222.023,322.2', getUnits=True)



## I should wrap this in a __main__ section
if __name__ == '__main__' and False:
  # Initialize the args
  start = datetime.now()
  args = argv.arg(description='Python GCode modifications',
                  getFile=True, # get gcode to process
                  getMultiFiles=True, # accept any number of files
                  otherOptions=OPTIONS, # Install some nice things
                  getDevice=False) # We dont need a device


  # optimize each file in the list
  for gfile in args.gcode:
    # only process things not processed before.
    # c = re.match(r'(?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap)', gfile.name)
    c = re.match(r'(.+)(\.tap)', gfile.name)
    if c: # either a drill.tap or etch.tap file
      mod(gfile)

  print '%s finished in %s'%(args.name,deltaTime(start))
