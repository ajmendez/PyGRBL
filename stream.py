#!/usr/bin/env python
# stream.py : A simple streamer
# [2012.01.31] Mendez

import re, sys, time
from datetime import datetime,timedelta
from lib.clint.textui import puts, colored, progress
from lib import argv
from lib.communicate import Communicate
from lib.util import deltaTime

RX_BUFFER_SIZE = 128

# Initialize the args
args = argv.arg(description='Simple python GRBL streamer', 
                getFile=True)

# Let go!
start = datetime.now()
puts(colored.blue(' Starting file: %s \n at %s'%(args.gcode.name, start)))

# read the full file and then close so that it cannot change.
# I am pretty sure even at 1M lines, I should be able to hold this in mem
lines = args.gcode.readlines()
args.gcode.close()

# get a serial device and wake up the grbl, by sending it some enters
with Communicate(args.device, args.speed, timeout=args.timeout,
                 debug=args.debug,
                 quiet=args.quiet) as serial:
  
  inBuf = [] # array of length of lines in buffer
  for i,line in enumerate(progress.bar(lines)):
    # Strip comments/spaces/new line, capitalize, and add line ending
    l = re.sub('\s|\(.*?\)','',line.strip()).upper()+'\n'  

    # if this was a comment or blank line just go to the next one
    if len(l.strip()) == 0:
      continue
    
    inBuf.append(len(l))
    out = ''
    # if the serial is has text and we have not filled the buffer
    while sum(inBuf) >= RX_BUFFER_SIZE-1 | serial.inWaiting():
      tmp = serial.readline().strip()
      # puts(colored.green('\ni: %d l: %s\n'%(i,l)))
      # puts(colored.green('temp: '+tmp+'\n'))
      if (tmp.find('ok') < 0 or tmp.find('error') > 0) and (len(tmp) > 0):
        puts(colored.red(' DEBUG: %d - %s'%(i, tmp)+' '*30))
        # If we got here, probably debugging, check that gcode is not in return
        # echo, and just move on.
        if args.debug:
          out += 'DEBUG'
          inBuf.pop(0)
      else:
        out += tmp
        inBuf.pop(0)
    
    #  send the command
    serial.write(l)
    if not args.quiet:
      puts(colored.blue('[%04d][Sent: %s][Buf:%3d]'%(i,l.strip().rjust(30),sum(inBuf))) +
           colored.green(' Rec: %s'%(out))+' '*12)

  # It seems everything is ok, but dont reset everything untill buffer completes
  puts(
    colored.green('''
  gCode finished streaming!
      Finished at: %s
      RunTime: %s'''%(datetime.now(), deltaTime(start))) + 
    colored.red('''
  !!! WARNING: Please make sure that the buffer clears before finishing...''') )
  raw_input('<Press any key to finish>')
  raw_input('   Are you sure? Any key to REALLY exit.')