#!/usr/bin/env python
# communicate.py : a simple serial device that can be a fake device.
# [2012.07.30] - Mendez

# [System]
import serial
import time
import readline

# [Installed]
from clint.textui import puts, colored

# [Package]


class Communicate():
  '''A simple wrapper around a serial device to communicate with GRBL device.
  Setup some nice defaults too'''
  def __init__(self, device, speed, 
               timeout=None,
               debug=False, 
               quiet=False):
    '''Start the serial device and set some nice commands to the grbl device
    so that it is in a nice state'''
    self.timeout = timeout
    self.debug = debug
    self.quiet = quiet
    
    # select the right serial device
    if debug:
      self.serial = FakeSerial()
    else:
      self.serial = serial.Serial(device, speed, timeout=timeout)
    
    if not quiet: 
      print('Initializing grbl at device: {}'.format(device))
      print(' Please wait 1 second for device...')
    
    self.serial.write("\r\n\r\n") # wake up the device 
    if not debug:
      self.wait(1.0) # Wait for the device to wake up
    self.serial.flushInput()
    
    # Run some commands to ensure that it is in a stable state.
    self.setup()
  
  
  def setup(self, homemachine=True):
        '''Asks the user if should home / run from current location'''
        while homemachine:
          x = raw_input('Should we home the machine? [y(es)]/n(o)').strip()
          if 'y' in x:
            self.run('$H (Home The Machine)')
            homemachine = False
          elif 'n' in x:
            self.run('$X (Use current location.)')
            homemachine = False
          else:
            puts(colored.red('Incorrect button pressed.'))
        
        # Set some nice defaults -- should be moved into an init block
        self.run(' ')
        self.run('$ (Current Settings)')
        self.run('G20 (Inches)')
        self.run('G90 (Absolute)')
  
  def wait(self, timeout=None):
    if timeout is None:
        timeout = self.timeout
    time.sleep(timeout)
  
    
  def run(self, cmd, singleLine=False):
    '''Extends either serial device with a nice run command that prints out the
    command and also gets what the device responds with.'''
    puts(colored.blue(' Sending: [%s]'%cmd ), newline=(not singleLine))
    # self.write(cmd+'\n')
    self.serial.write(cmd)
    self.wait()
    
    # Get the data sent back
    out = ''
    while self.serial.inWaiting(): 
      out += self.serial.readline()
    
    # Print output to the screen
    if out != '':
      if singleLine:
        tmp = '['+', '.join([o for o in out.splitlines()])+']'
      else:
        tmp = ''.join([' | '+o+'\n' for o in out.splitlines()])
      puts(colored.green(tmp), newline=(not singleLine))
      
  def __enter__(self):
    '''With constructor'''
    return self
  
  def __exit__(self, type, value, traceback):
    self.serial.setDTR(False)
    self.wait(0.022) # a short wait to ensure everything is ok
    self.serial.setDTR(True)
    self.serial.close()
    return isinstance(value, TypeError)
  
  def __getattr__(self, name):
    '''I want this to act like the serial device, so for
    any attribute that is not run above, this will attempt
    to load it from the serial object.'''
    try:
      return getattr(self.serial, name)
    except KeyError:
      raise AttributeError(name)




class FakeSerial():
    '''This is a fake serial device that mimics a true serial devie and 
    does fake read/write.'''
    def __init__(self):
        '''init the fake serial and print out ok'''
        self.waiting = 1  # If we are waiting
        self.ichar = 0    # index of the message
        self.msg = 'ok'   # default happy message
    
    def __getattr__(self, name):
        print 'DEBUG SERIAL: %s'%(name)
        return self.sprint
        
    def sprint(self, *args, **kwargs):
        '''a default function / attribute to be a robustly ignorant 
        fake serial device'''
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
            out = '\n'
        return out
        
    def readline(self):
        '''Return any message'''
        time.sleep(0.1)
        self.waiting = 0
        return self.msg
        
    def inWaiting(self):
        '''Are we done pushing out a msg? '''
        out = self.waiting
        if self.waiting == 0:
            self.waiting = 1
        return out