#!/usr/bin/env python
# args.py : a simple argument parser for the command line tools
# [2012.07.30] - Mendez

import argparse, sys
# from clint.textui import colored, puts, indent
from glob import glob
from util import error


def arg(description=None, getDevice=True, getFile=False, defaultSpeed=9600):
  '''This is a simple arugment parsing function for all of the command line tools'''
  if not description:
    description='python grbl arguments'
  
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('-q','--quiet',
                      action='store_true',
                      default=False,
                      help='suppress output text')
  parser.add_argument('-d','--debug',
                      action='store_true',
                      default=False,
                      help='[DEBUG] use a fake Serial port that prints to screen')
  parser.add_argument('-s','--speed',
                      # action='store_true',
                      default=defaultSpeed,
                      type=int,
                      help='Serial port speed [%d]'%(defaultSpeed))
                      
  # by default just get the device, otherwise get a file first since device can be found.
  if getFile:
    parser.add_argument('gcode', 
                        type=argparse.FileType('r'), 
                        help='gCode file to be read and processed.')
  if getDevice:
    parser.add_argument('device',
                        nargs='?',
                        # action='store_true',
                        default=False,
                        help='The GRBL device to drive')
  args = parser.parse_args()
  
  # lets see if we can find a default device to connect too.
  if args.debug:
    args.device='fakeSerial'
  
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
      
  
  return args
