#!/usr/bin/env python
# argv.py : a simple argument parser for the command line tools
# [2012.07.30] - Mendez

# [System]
import argparse
import sys
from glob import glob

# [Installed]

# [Package]
from pygrbl import util


def getdefaultdevice():
    '''Lets try to find a default serial device.  Generally a computer has
    a single GRBL/arduino connected.  Returns a list of possible devices'''
    # Where they generally are: 
    devs = [
        '/dev/tty.usb*', # Linux Arduino UNO?
        '/dev/ttyACM*',  # Arduino Duemilanove
        '/dev/tty.PL*',  # Prolific USB-to-Serial :: PL2303
        '/dev/ttyUSB*'   # OSX Arduino UNO?
        
    ]
    
    # Run though the list and see if this system has any of them
    # There must be a way to do this in windows, but ?!
    founddevs = []
    for d in devs:
      dev = glob(d)
      if len(dev) > 0:
          founddevs.extend(dev)
    
    return founddevs

class ArgParse(argparse.ArgumentParser):
  def error(self, message):
    self.print_help()
    util.error(message)


def arg(description=None, getDevice=True, 
        defaultSpeed=9600, defaultTimeout=0.50,
        getFile=False, getMultiFiles=False):
  '''This function simplifies the argument parsing for each of the scripts in the
  bin directory.  This is basically a wrapper around the argparse libary
  that simplifies the defaults since they are generally the same for each item
  
  @description -- A sentence that describes the the script. This is accessed when
                  you run the function without required arguments or -h
  @getDevice [True] -- This script needs to get a device
  '''
  if not description:
    description='python grbl arguments'
  
  # parser = argparse.ArgumentParser(description=description)
  parser = ArgParse(description=description)
  
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
  # this means we can do a star and grab everything from the command line
  if getFile:
    if getMultiFiles:
      name = 'gcode_file ... gcode_file'
      nargs = '+'
    else:
      name = 'gcode'
      nargs = 1
    parser.add_argument(name, 
                        nargs=nargs,
                        type=argparse.FileType('r'), 
                        help='gCode file to be read and processed.')
  
  # if we want a device get an optional speed / and a device
  if getDevice:
    parser.add_argument('-s','--speed',
                        default=defaultSpeed,
                        type=int,
                        help='Serial port speed in baud. [%d]'%(defaultSpeed))
    parser.add_argument('-t','--timeout',
                        default=defaultTimeout,
                        type=float,
                        help='''Serial Port Timeout: Amount of time to wait
                                before gathering data for display [{:0.2f}]
                                '''.format(defaultTimeout))
    
    parser.add_argument('device',
                        nargs='?',
                        # action='store_true',
                        default=False,
                        help='''GRBL serial dev. Generally this should be
                                automatically found for you. You should specify
                                this if it fails, or your have multiple boards 
                                attached.''')  
  
  # Parse the arguments & save name
  args = parser.parse_args()
  args.name = sys.argv[0]

  # if we want to get a single file then
  if (getFile) and (not getMultiFiles):
    args.gcode = args.gcode[0]
  
  # For debbuging use a fake serial device
  if args.debug: 
    args.device = 'fakeSerial'
  
  # If one has not defined as device from the command, or using 
  # a fake one then try to get a default one. Error if we 
  # find many serial devices or none
  if getDevice and not args.device:
    devices = getdefaultdevice()
    ndev = len(devices)
    
    # error if we found more than 1 or no devices
    if ndev == 1:
      args.device = devices[0]
    else:
      parser.print_help()
      util.error('Found {:d} device(s) : {} -- '
                 'You need to connect a device, or specify which device you '
                 'want to use.'''.format(ndev, devices))
  
  
  return args
