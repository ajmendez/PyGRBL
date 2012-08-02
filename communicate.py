#!/usr/bin/env python
# communicate.py : a simple serial device that can be a fake device.
# [2012.07.30] - Mendez

import serial, time

def initSerial(device, speed, debug=False, quiet=False):
  if debug:
    s = FakeSerial()
  else:
    s = serial.Serial(device,speed)
  
  if not quiet:
    print "Initializing grbl at device: %s\n  Please wait 1 second for device..."%(device)
  s.write("\r\n\r\n")
  # Wait for grbl to initialize and flush startup text in serial input
  if not debug:
    time.sleep(1)
  s.flushInput()
  
  return s




class FakeSerial():
    '''This is a fake serial device that mimics a true serial devie and does read/write.'''
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
    def flushInput(self):
      '''Nothing to do but ignore the input which we are aready doing'''
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
    def readline(self):
      time.sleep(0.1)
      self.waiting = 0
      return self.msg
    def inWaiting(self):
        '''Are we done pushing out a msg? '''
        out = self.waiting
        if self.waiting == 0:
            self.waiting = 1
        return out