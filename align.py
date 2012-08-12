#!/usr/bin/env python
# align.py : Align the drill bit with the keyboard
# [2012.08.03] Mendez written
import readline, sys, re, time
from lib.clint.textui import colored, puts
from lib import argv
from lib.communicate import Communicate
from lib.terminal import Terminal

QUIT = ['q','Q']
UPDATE =['u','U']
UP = ['\x1b[B']
DOWN = ['\x1b[A']
RIGHT = ['\x1b[D']
LEFT = ['\x1b[C']
RAISE = ['a','A']
LOWER = ['z','Z']

# I might also want to implement this
# from curses import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT

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
  '''To simplify the code below, 
    I have this function which reads in the 
    direction and which direction to go, and
    then it pushes some gcode to the grbl'''
  c = re.match(r'(?P<axis>X|Y|Z)(?P<dir>\+|\-)',direction, re.IGNORECASE)
  if not c: puts(colored.red('FAILED MOVE!!! check code: %s'%direction))
  
  sign = '' if c.group('dir')=='+' else '-'
  location[c.group('axis')] += float(sign+'1')*(moveLength)
  serial.run('G%02i %s%s%0.3f'%(0, # gcode cmd value using MOVE
                                c.group('axis'), # X/Y/Z
                                sign, #Not sure if gcode handles '+'/'-' so ''/'-'
                                moveLength),
             singleLine=True)
  # Give the user some idea where we are.
  puts(colored.blue('(%s)'%', '.join(['%.3f'%location[k] for k in location])))
  # isAt = ', '.join(['%s=%.3f'%(a,location[a]) for a in location])
  # puts(colored.blue('    Currently at: %s'%isAt))
 
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
args = argv.arg(description='Simple python alignment tool',
                defaultTimeout=0.25)

# Using with logic to handle tear down and the sort.
with Communicate(args.device, args.speed, timeout=args.timeout,
                 debug=args.debug,
                 quiet=args.quiet) as serial:
  # lets begin by giving the user some nice information
  puts(colored.blue(HELP))
  for line in startCommand.splitlines():
    serial.run(line)
  
  # Not only do we need to talk to the serial device, we also need 
  # some input from the user, so create a terminal object to do this.
  print '<waiting for key>'
  with Terminal() as terminal:
    while True:
      # if not terminal.isData():
      #   # time.sleep(0.25)
      #   continue
      c = terminal.getch()
      # if not c: continue
      # print 'noop[%s]'%repr(c) # it is nice to give the user some idea what happened
      # print 'TYPED: %s'%repr(c)
      # if not c: time.sleep(0.25)
      if   c in   QUIT: sys.exit() # Quit the program
      elif c in UPDATE: moveLength = update()
      elif c in     UP: move('X-')
      elif c in   DOWN: move('X+')
      elif c in  RIGHT: move('Y-')
      elif c in   LEFT: move('Y+')
      elif c in  RAISE: move('Z+')
      elif c in  LOWER: move('Z-')
      else: pass
      # else : print 'noop[%s]'%repr(c) # it is nice to give the user some idea what happened
      print '<waiting for key>'
    

# ok now grab a character and decide what to do.
# while 1:
#   print '<waiting for key>'
#   c = getch()
#   # if not c: time.sleep(0.25)
#   if   c in   QUIT: sys.exit() # Quit the program
#   elif c in UPDATE: moveLength = update()
#   elif c in     UP: move('X-')
#   elif c in   DOWN: move('X+')
#   elif c in  RIGHT: move('Y-')
#   elif c in   LEFT: move('X+')
#   elif c in  RAISE: move('Z+')
#   elif c in  LOWER: move('Z-')
#   else : print 'noop[%s]'%repr(c) # it is nice to give the user some idea what happened

serial.close()
