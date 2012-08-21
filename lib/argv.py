#!/usr/bin/env python
# argv.py : a simple argument parser for the command line tools
# [2012.07.30] - Mendez

import argparse, sys
# from clint.textui import colored, puts, indent
from glob import glob
from util import error


def arg(description=None, getDevice=True, 
        defaultSpeed=9600, defaultTimeout=0.50,
        getFile=False, getMultiFiles=False,
        otherOptions=None):
  '''This is a simple arugment parsing function for all of the command line tools'''
  if not description:
    description='python grbl arguments'
  
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('-q','--quiet',
                      action='store_true',
                      default=False,
                      help='suppress output text -- Working in some scripts.')
  parser.add_argument('-d','--debug',
                      action='store_true',
                      default=False,
                      help='[DEBUG] use a fake Serial port that prints to screen')
                      
  # by default just get the device
  # HOWEVER if we want a file to be run, get it FIRST
  if getFile:
    nargs = '+' if getMultiFiles else 1
    parser.add_argument('gcode', 
                        nargs=nargs,
                        type=argparse.FileType('r'), 
                        help='gCode file to be read and processed.')
  
  # if we want a device get an optional speed / and a device
  if getDevice:
    parser.add_argument('-s','--speed',
                        # action='store_true',
                        default=defaultSpeed,
                        type=int,
                        help='Serial port speed in baud. [%d]'%(defaultSpeed))
    parser.add_argument('-t','--timeout',
                        # action='store_true',
                        default=defaultTimeout,
                        type=float,
                        help='Serial Port Timeout: Amount of time to wait before gathering data for display [%.2f]'%(defaultTimeout))
    
    parser.add_argument('device',
                        nargs='?',
                        # action='store_true',
                        default=False,
                        help='GRBL serial dev. Generally this should be automatically found for you. You should specify this if it fails, or your have multiple boards attached.')  
  
  # For any specalized options lets have a general import method
  if otherOptions:
    for item in otherOptions:
      args = otherOptions[item].pop('args')
      parser.add_argument(*args, **otherOptions[item])
  

  args = parser.parse_args()
  
  # lets see if we can find a default device to connect too.
  if args.debug: args.device='fakeSerial'
  if (getFile) and (not getMultiFiles): args.gcode = args.gcode[0]
  if getDevice and not args.device:
    # Where they generally are: 
    devs = ['/dev/tty.usb*','/dev/ttyACM*','/dev/tty.PL*','/dev/ttyUSB*']
    founddevs = []
    for d in devs:
      dev = glob(d)
      if len(dev) > 0 : founddevs.extend(dev)
    # ok we found something or we should fail
    if len(founddevs) == 1:
      args.device = founddevs[0]
    else:
      parser.print_help()
      error('Found %d device(s) -- You need to connect a device, update %s, or specify wich device you want to use.'%(len(founddevs),sys.argv[0]))
  
  
  args.name = sys.argv[0]
  
  return args
