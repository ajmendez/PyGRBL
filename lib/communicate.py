#!/usr/bin/env python
# communicate.py : a simple serial device that can be a fake device.
# [2012.07.30] - Mendez

import serial, time, readline
from clint.textui import puts, colored



class Communicate():
  def __init__(self, device, speed, debug=False, quiet=False, timeout=None):
    # select the right serial device
    if debug: s = FakeSerial()
    else:     s = serial.Serial(device, speed, timeout=timeout)
    
    if not quiet: print '''Initializing grbl at device: %s
  Please wait 1 second for device...'''%(device)
    s.write("\r\n\r\n")
    if not debug: time.sleep(1.0)
    s.flushInput()
    self.timeout = timeout
    self.s = s
    self.run(' ')
    self.run('$ (Current Settings)')
    self.run('G20 (Inches)')
    self.run('G90 (Absolute)')
    
    
  def run(self, cmd, singleLine=False):
    '''Extends either serial device with a nice run command that prints out the
    command and also gets what the device responds with.'''
    puts(colored.blue(' Sending: [%s]'%cmd ), newline=(not singleLine))
    self.write(cmd+'\n')
    out = ''
    time.sleep(self.timeout)
    # while s.inWaiting() > 0: out += s.read(10)
    while self.inWaiting() > 0: out += self.readline()
    if out != '':
      if singleLine:
        puts(colored.green('[%s]'%', '.join([o for o in out.splitlines()])),
             newline=False)
      else:
        puts(colored.green(''.join([' | '+o+'\n' for o in out.splitlines()])))

  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    self.s.setDTR(False)
    time.sleep(0.022)
    self.s.setDTR(True)
    self.s.close()
    return isinstance(value, TypeError)
  
  def __getattr__(self, name):
    '''if no command here, see if it is in serial.'''
    try:
      return getattr(self.s, name)
    except KeyError:
      raise AttributeError(name)




class FakeSerial():
    '''This is a fake serial device that mimics a true serial devie and 
    does fake read/write.'''
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