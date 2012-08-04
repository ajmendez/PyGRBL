#!/usr/bin/env python
# command.py : A simple command prompt
# [2012.08.02] - Mendez: cleaned up using my libraries
# [2012.01.10] - SJK: original version
import re, readline, time
from lib import communicate, argv

# Initialize the args
args = argv.arg(description='Simple python grbl command')

# get a serial device and wake up the grbl, by sending it some enters
serial = communicate.initSerial(args.device, args.speed, debug=args.debug, quiet=args.quiet)


# now we send commands to the grbl, and wait waitTime for some response.
while True:
  # Get some command
  x = raw_input('grbl> ').strip()
  if x in ['q','exit','quit']: break
  
  # run it if is not a quit switch
  serial.run(x)

# Close file and serial port
serial.close()