#!/usr/bin/env python
# util.py : some nice things
# [2012.07.30] - Mendez
import sys, os, termios, fcntl
from clint.textui import colored, puts, indent
from datetime import datetime
from math import sqrt


def error(message):
  '''Nice little error message for the user that causes a quit'''
  puts(colored.red('\n !!! '+message))
  sys.exit(1)



def deltaTime(start):
  '''From a start datetime object get a nice string of 'x hours, y minutes, z seconds'
  of time passed since the start. '''
  
  diff = datetime.now() - start
  # seconds = diff.seconds # limited to 1 second, so lets get fractions
  seconds = diff.microseconds/float(10**6)
  out = []
  epocs = [ [3600,'hour'],
            [60,'minute'],
            [1,'second'],
            [0.001,'milisecond'] ]
  factors,tmp = zip(*epocs)
  while seconds > min(factors):
    for factor, noun in epocs:
      if seconds >= factor:
        delta = seconds/factor
        if delta > 1: noun +='s'
        out.append('%d %s'%(delta,noun))
        seconds -= factor*(delta)
  
  return ', '.join(out)


def distance(A,B):
  '''euclidean distance of two lists. TODO should be generalized...'''
  return sqrt(sum([pow(alpha-beta,2) for alpha,beta in zip(A,B)]))


def uniqify(seq, idfun=None): 
   '''order preserving uniq function'''
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


def getch():
  '''Get a character from the terminal.
  Accepts escape sequences and also returns them.
  This kills the cpu, try getchar.
  I found this off of stackoverflow'''
  fd = sys.stdin.fileno()
  
  # Enables some nice bits for the terminal so that we can grab the charcers 
  # without blocking things and saving the old flags
  oldterm = termios.tcgetattr(fd)
  newattr = termios.tcgetattr(fd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, newattr)
  
  oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
  
  try:        
    while 1:            
      try:
        # Try to get at most 10 bytes of an escape sequence
        c = sys.stdin.read(10)
        break
      except IOError: 
        pass
  finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
  return c


import tty,select
class Terminal():
  def isData(self):
    '''Is there data ready to process'''
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
  
  def __enter__(self):
    self.oldterm = termios.tcgetattr(sys.stdin)
    
    self.fd = sys.stdin.fileno()
    self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
    newattr = termios.tcgetattr(self.fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(self.fd, termios.TCSANOW, newattr)
    fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
    
    tty.setcbreak(sys.stdin.fileno())
    return self
  def __exit__(self, type, value, traceback):
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.oldterm)
    fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
    return isinstance(value, TypeError)
  def getline(self):
    if self.isData():
      c = sys.stdin.read(3)
      while self.isData(): sys.stdin.read(1)
      return c
    
    
  def __Xenter__(self, type, value, traceback):
    '''Build it up for a with'''
    self.fd = sys.stdin.fileno()
    self.oldterm = termios.tcgetattr(self.fd)
    self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
    
    # Enables some nice bits for the terminal so that we can grab the charcers 
    # without blocking things
    newattr = termios.tcgetattr(self.fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(self.fd, termios.TCSANOW, newattr)
    fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
    return self
  
  def __Xexit__(self, type, value, traceback):
    '''Tear everything down'''
    termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
    fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
    return isinstance(value, TypeError)
  
  def Xgetline(self):
    '''Attempts to gather a line'''
    while 1:
      try: 
        c = sys.stdin.read(10)
        break
      except IOError:
        pass
    return c
    