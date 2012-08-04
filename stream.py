#!/usr/bin/env python
# stream.py : A simple streamer
# [2012.01.31] Mendez

import re, sys, time
from datetime import datetime,timedelta
from clint.textui import puts,indent,colored,progress
import communicate, argv
from util import deltaTime

RX_BUFFER_SIZE = 128

# Initialize the args
args = argv.arg(description='Simple python GRBL streamer', getFile=True)

# get a serial device and wake up the grbl, by sending it some enters
s = communicate.initSerial(args.device, args.speed, debug=args.debug, quiet=args.quiet)

start = datetime.now()
with indent(1,quote='|'):
  puts(colored.blue('Starting file: %s \n at %s'%(args.gcode.name, start)))

verbose = not args.quiet

# read the full file and then close so that it cannot change.
# I am pretty sure even at 1M lines, I should be able to hold this in mem
lines = args.gcode.readlines()
args.gcode.close()

inBuf = [] # array of length of lines in buffer
for i,line in enumerate(progress.bar(lines)):
  # Strip comments/spaces/new line, capitalize, and add line ending
  l = re.sub('\s|\(.*?\)','',line.strip()).upper()+'\n' 

  # if this was a comment or blank line just go to the next one
  if len(l) == 0: continue
  
  inBuf.append(len(l))
  out = ''
  nOk = 0
  # if the serial is has text and we have not filled the buffer
  while sum(inBuf) >= RX_BUFFER_SIZE-1 | s.inWaiting() :
    tmp = s.readline().strip() # grab a line from grbl
    if tmp.find('ok') < 0 and tmp.find('error') < 0:
      with indent(1): puts(' DEBUG: '%(tmp))
    else:
      out += tmp
      inBuf.pop(0)
    #  send the command
    s.write(l)
    if verbose:
      with indent(1, quote='|'):
        puts(colored.blue('[%d][Sent: %s][Buf:%d]'%(i,l.strip(),sum(inBuf))) +
             colored.green('[Rec:%s]'%(out))+' '*12)

# It seems everything is ok, but dont reset everything untill buffer completes
puts(colored.green('gCode finished streaming! \n Finished at: %s \n RunTime: %s'%(datetime.now(), deltaTime(start))))
puts(colored.red('WARNING: Please make sure that the buffer clears before finishing...'))
raw_input('Press any key to finish')
raw_input(' Are you sure? Any key to REALLY exit.')
s.close()