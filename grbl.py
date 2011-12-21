#!/usr/bin/env python
####################
## Mendez
## [2011.12.11]
####################
import serial, time, readline, sys, getopt, curses


def gdebug(getargv=False):
    DEBUG=False
    options,remainder = getopt.gnu_getopt(sys.argv[1:], 'd')
    for opt, arg in options:
        if opt == '-d':
            DEBUG=True
    if getargv:
        remainder.insert(0,sys.argv[0])
        return (DEBUG, remainder)
    return DEBUG



class fakeserial():
    '''I need a a debug serial object.'''
    def __init__(self):
        '''init the fake serial and print out ok'''
        self.waiting=1  # If we are waiting
        self.ichar=0    # index of the character that we are on.
        self.msg='ok'   # the message that we print when we get any command
    
    def __getattr__(self, name):
        print 'DEBUG SERIAL: %s'%(name)
        return self.p
    def p(self,x=None,y=None):
        '''Lambda probably makes this better.'''
        pass
    def write(self, x):
        ''' this is pretty noisy so lets ignore it quietly.'''
        pass
    def read(self, n=1):
        '''Return the message n characters at a time.'''
        if self.ichar < len(self.msg):
            out = self.msg[self.ichar:self.ichar+n]
            self.ichar += n
        else:
            self.ichar = 0
            self.waiting = 0
            out='\n'
        return out
    
    def inWaiting(self):
        '''Are we done pushing out a msg? '''
        out = self.waiting
        if self.waiting == 0:
            self.waiting = 1
        return out


class grbl:
  def __init__(self, dev=None, speed=None, debug=False, waittime=0.5):
    '''Starts the Serial device'''
    if not dev: dev='/dev/tty.usbmodem1d11'
    if not speed: speed=9600
    self.waittime = waittime
    self.debug = debug
    
    if debug:
       self.waittime=0.1
    
    # Start the serial port
    if debug:
        self.s = fakeserial()
    else:
        self.s = serial.Serial(dev,speed)
    
    self.s.open()
    self.s.isOpen()
    
    # Wake up grbl
    self.s.write("\r\n\r\n")
    time.sleep(1)   # Wait for grbl to initialize
    self.s.flushInput()  # Flush startup text in serial input
    
  def run(self, cmd, echocmd=False, cmdprefix='Sending'):
    '''Run a command: '''
    if echocmd:
      print '%s: %s'%(cmdprefix,cmd)
    self.s.write(cmd+'\n')
    out=''
    time.sleep(self.waittime)
    while self.s.inWaiting() > 0:
      out += self.s.read(1)
    if out != '':
      print '\n'.join([' |  ' + o for o in out.splitlines()])
  
  def quit(self):
    '''Shuts down the system'''
    self.s.close()
  
  def origin(self):
    '''Make sure to start with everything zeroed out.'''
    # self.screen = curses.initscr()
    
    axes = ['x','y','z']
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
    raw_input(">>>  Press <Enter> to finish  <<<")
    
    