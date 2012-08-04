#!/usr/bin/env python
# align.py : Align the drill bit with the keyboard
# [2012.08.03] Mendez written
import readline, sys, re, time
from util import getch
from lib.clint.textui import colored, puts, indent
from lib import argv, communicate

QUIT = ['q','Q']
UPDATE =['u','U']
UP = ['\x1b[A']
DOWN = ['\x1b[B']
RIGHT = ['\x1b[C']
LEFT = ['\x1b[D']
RAISE = ['a','A']
LOWER = ['z','Z']

# I might also want to implement this
# curses.KEY_UP   
# curses.KEY_DOWN 
# curses.KEY_LEFT 
# curses.KEY_RIGHT

startCommand = '''\
G20 (Inches)
G91 (Incremental)
G0 X0.000 Y0.000 Z0.000
'''
HELP = '''\
Board Alignment Keys:
q/Q        : Quit
u/U        : Update moveLength -- Amount to nudge 
Arrow Keys : Move in X [Forward/Back]
                     Y [Left/Right]
a/A / z/Z  : Move in Z [Raise/Lower]
'''

moveLength = 0.100 # Inches [0.100] : amount to move use update(), to change
location = dict(X=0.0, Y=0.0, Z=0.0) # store the current location inches



# Some helper functions, scroll down for tasty bits
def move(direction=''):
  '''Figures out what to move'''
  c = re.match(r'(?P<axis>X|Y|Z)(?P<dir>\+|\-)',direction, re.IGNORECASE)
  if not c: puts(colored.red('FAILED MOVE!!! check code: %s'%direction))
  
  sign = '' if c.group('dir')=='+' else '-'
  location[c.group('axis')] += float(sign+'1')*(moveLength)
  s.run('G%02i %s%s%0.3f'%(0, # gcode cmd value using MOVE
                           sign, #Not sure if gcode handles '+'/'-' so ''/'-'
                           c.group('axis'), # X/Y/Z
                           moveLength) )
  # Give the user some idea where we are.
  isAt = ', '.join(['%s=%.3f'%(a,location[a]) for a in location])
  puts(colored.blue('    Currently at: %s'%isAt))
 
def update():
  '''Update the moveLength for each command'''
  # easier to store this way, but unzip to make nice
  tmp =(('mm',1.0/25.4),('inch',1.0),('mil',1.0/1000.0))
  units, scales = zip(*tmp)
  
  # tell the user what is going on.
  puts(colored.green('''\
Current Nudge length: %.3f inch [Default: 100mil].  
  Example input: "0.020inch", "20mil", "30mm"
  Possible Units: %s'''%(moveLength, ', '.join(units)) ))
  
  # get the input and clean
  userValue = raw_input('Update nudge length to: ')
  value = re.sub(r'\s','',userValue.strip()) # Remove Whitespace
  
  # match to units and values
  c = re.match(r'(?P<num>\d?\.?\d)(?P<unit>'+'|'.join(units)+')', value, re.IGNORECASE)
  
  # if the user was bad just go back
  if not c or not c.group('unit') in units:
    puts(colored.red('Failed to update, try again with update key...'))
    return moveLength
  
  # Update the moveLength which is in inches by using the right scale for the unit
  newLength = float(c.group('num'))*scales[units.index(c.group('unit'))]
  puts(colored.blue(' > moveLength is now: %.3f inch\n'%newLength))
  return newLength





# Get the arguments passed into the program
args = argv.arg(description='Simple python alignment tool')

# Setup the serial device

s = communicate.initSerial(args.device, args.speed, debug=args.debug, quiet=args.quiet)


# lets begin by giving the user some nice information
puts(colored.blue(HELP))
for line in startCommand.splitlines():
  s.run(line)

# ok now grab a character and decide what to do.
while 1:
  print '<waiting for key>'
  c = getch()
  if not c:
    time.sleep(waittime)
  if c in 'q': sys.exit() # Quit the program
  elif c in UPDATE: moveLength = update()
  elif c in    UP: move('X-')
  elif c in  DOWN: move('X+')
  elif c in RIGHT: move('Y-')
  elif c in  LEFT: move('X+')
  elif c in RAISE: move('Z+')
  elif c in LOWER: move('Z-')
  else: print 'noop', # it is nice to give the user some idea what happened
    # print "PRINT: ",repr(c) 