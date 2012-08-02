#!/usr/bin/env python
# bufferstream.py
#  Buffers the stream to ensure not code stream starvation.
# [2012.01.10] - SJK
import re, readline, time
import communicate, args
from glob import glob
from clint.textui import puts,indent,colored

# Initialize the args
args = args.arg(description='Simple python grbl command')

# get a serial device and wake up the grbl, by sending it some enters
s = communicate.initSerial(args.device, args.speed, debug=args.debug, quiet=args.quiet)


# now we send commands to the grbl, and wait waitTime for some response.
waittime = 0.25
while True:
  out=''
  x = raw_input('grbl> ').strip()
  if x in ['q','exit','quit','fuckoff']: break
  with indent(1):
    puts(colored.blue('Sending: [%s]'%(x)))
    s.write(x+'\n')
    
    # wait for device to respond
    time.sleep(waittime)
    
    # collect message
    # while s.inWaiting() > 0: out += s.read(1)
    while s.inWaiting() > 0: out += s.readline()
    if out != '':
      with indent(3, quote=colored.green(' | ')):
        puts(colored.green('\n'.join([o for o in out.splitlines()])))


# Close file and serial port
s.close()