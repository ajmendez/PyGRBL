#!/usr/bin/env python
####################
## Mendez
## [2011.12.11]
####################
import serial, time, readline

class grbl:
  def __init__(self, dev=None, speed=None):
    '''Starts the Serial device'''
    if not dev: dev='/dev/tty.usbmodem1d11'
    if not speed: speed=9600
    
    # Start the serial port
    self.s = serial.Serial(dev,speed)
    self.s.open()
    self.s.isOpen()
    
    # Wake up grbl
    self.s.write("\r\n\r\n")
    time.sleep(2)   # Wait for grbl to initialize
    self.s.flushInput()  # Flush startup text in serial input
    
  def run(self, cmd, echocmd=False, cmdprefix='Sending'):
    '''Run a command: '''
    if echocmd:
      print '%s: %s'%(cmdprefix,cmd)
    self.s.write(cmd+'\n')
    out=''
    time.sleep(0.5)
    while self.s.inWaiting() > 0:
      out += self.s.read(1)
    if out != '':
      print '\n'.join([' |  ' + o for o in out.splitlines()])
  
  def quit(self):
    '''Shuts down the system'''
    self.s.close()
  
  def origin(self):
    '''Make sure to start with everything zeroed out.'''
    axes=['x','y','z']
    self.run('G21') # milimeters
    self.run('G90') # Absolute
    for axis in axes:
      print 'For axis %s use the left and right arrow keys to locate the zero then press [enter]'%(axis)
      
    # 9:21 - 6128
    # 9:25 - 6772
    #~200 lines per minute
    
  def runfile(self, gfile=None):
    '''Run a specific G-code file'''
    f = open(gfile,'r')
    lines = f.readlines()
    f.close()
    for i,line in enumerate(lines):
      l = line.strip() # Strip all EOL characters for streaming
      p = i/float(len(lines))*100
      self.run(l, echocmd=True, cmdprefix='[%2d]Sending'%(p))
    
    # Wait here until grbl is finished to close serial port and file.
    raw_input("  Press <Enter> to finish")
    
    