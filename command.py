#!/usr/bin/env python
# command.py : A simple command prompt
# [2012.08.02] - Mendez: cleaned up using my libraries
# [2012.01.10] - SJK: original version
import re, readline, time
from lib import argv
from lib.communicate import Communicate

# Initialize the args
args = argv.arg(description='Simple python grbl command prompt for debuging the GRBL')

# get a serial device and wake up the grbl, by sending it some enters
with Communicate(args.device, args.speed, 
                 timeout=args.timeout,
                 debug=args.debug,
                 quiet=args.quiet,
                 home=args.home,
                 spindle=args.spindle) as serial:
  
  # now we send commands to the grbl, and wait waitTime for some response.
  while True:
    # Get some command
    x = raw_input('grbl> ').strip()
    if x in ['q','exit','quit']: break
  
    # run it if is not a quit switch
    serial.run(x)