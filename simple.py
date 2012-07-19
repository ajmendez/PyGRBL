#!/usr/bin/env python
# bufferstream.py
#  Buffers the stream to ensure not code stream starvation.
# [2012.01.10] - SJK
import serial, re, time, sys, argparse, readline
from glob import glob

RX_BUFFER_SIZE = 128

# Define command line argument interface
parser = argparse.ArgumentParser(description='Stream g-code file to grbl. (pySerial and argparse libraries required)')
# parser.add_argument('gcode_file', type=argparse.FileType('r'), help='g-code filename to be streamed')
parser.add_argument('-d','--device',action='store_true', default=None, help='serial device path')
parser.add_argument('-q','--quiet',action='store_true', default=False,help='suppress output text')
args = parser.parse_args()

# Lets automatically search for a arduino for osx / linux.
if not args.device:
  # Where they generally are: 
  devs = ['/dev/tty.usb*','/dev/ttyACM*','/dev/tty.PL*']
  founddevs = []
  for d in devs:
    dev = glob(d)
    if len(dev) > 0 : founddevs.extend(dev)
  # ok we found something or we should fail
  if len(founddevs) == 1:
    args.device = founddevs[0]
  else:
    parser.print_help()
    print '\n !!! Could not find a single or any device to use, please specify one.'
    sys.exit(1)

# Initialize
s = serial.Serial(args.device,9600)
verbose = True if args.quiet else  False

# Wake up grbl
print "Initializing grbl..."
s.write("\r\n\r\n")

# Wait for grbl to initialize and flush startup text in serial input
time.sleep(2)
s.flushInput()

waittime=0.5
while True:
  x = raw_input('cmd> ')
  if x.strip() == 'quit' or x.strip() == 'exit' or x.strip() == 'q':
    break
  print '  %s: %s'%('sending',x)
  s.write(x+'\n')
  
  out=''
  time.sleep(waittime)
  while s.inWaiting() > 0: out += s.read(1)
  if out != '':
    print '\n'.join([' |  ' + o for o in out.splitlines()])


# Close file and serial port
s.close()