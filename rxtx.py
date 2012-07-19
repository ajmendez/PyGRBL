#!/usr/bin/env python
import serial, re, time, sys, argparse, readline

parser = argparse.ArgumentParser(description='Watch a serial device')
parser.add_argument('device',  help='device', nargs='?')
parser.add_argument('speed', default=9600, help='speed', nargs='?')
parser.add_argument('-u','--user',action='store_true', default=False, help='user input')
args = parser.parse_args()
if not args.device:
  print args.device

s = serial.Serial(args.device,args.speed)

out=''
waittime=0.5
while True:
  if args.user:
    x = raw_input('cmd> ')
    if x.strip() == 'quit' or x.strip() == 'exit' or x.strip() == 'q':
      break
    if x.strip() == 'count':
      for i in range(1000):
        print ' counting: %i'%i
        s.write("%i\r\n"%(i))
        time.sleep(waittime)
    print '  %s: %s'%('sending',x)
    s.write(x+'\r\n')
    time.sleep(waittime)
  
  
  while s.inWaiting() > 0: out += s.read(1)
  if '\n' in out:
    print '\n'.join([' |  ' + o for o in out.splitlines()])
    out=''