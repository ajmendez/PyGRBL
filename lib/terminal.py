#!/usr/bin/env python
# terminal.py : some nice terminal things
# [2012.08.06] Mendez
import sys, os, termios, fcntl, tty, select


class Terminal():
  '''Terminal is a helper class to get access to a nonblocking character terminal
  you can use it with "with":
  with Terminal() as terminal:
    while 1:
      if terminal.isData():
        c = terminal.getch()
        # do things
  '''
  def isData(self):
    '''Is there data ready to process'''
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
  
  def waitForData(self):
    '''Is there data ready to process'''
    return select.select([sys.stdin], [], []) == ([sys.stdin], [], [])
  
  def echo(self):
    '''echo characters to screen'''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.oldterm)
    fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
  
  def noEcho(self):
    '''No display echo'''
    tty.setcbreak(self.fd)
  
  def wait(self):
    '''do not accept new characters'''
    termios.tcflow(self.fd,termios.TCIOFF)
    
  def accept(self):
    '''accept new chars'''
    termios.tcflush(self.fd, termios.TCIFLUSH)
    termios.tcflow(self.fd,termios.TCION)
  
  def __enter__(self):
    '''Set the sterminal to non blocking
    originally I was doing this with low level, but tty seems to be
    much better in general.
    Save the old parameters for resetting it though'''
    self.oldterm = termios.tcgetattr(sys.stdin)
    
    self.fd = sys.stdin.fileno()
    self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
    self.noEcho()
    # newattr = termios.tcgetattr(self.fd)
    # newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    # termios.tcsetattr(self.fd, termios.TCSANOW, newattr)
    # fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
    # tty.setcbreak(self.fd)
    return self
  def __exit__(self, type, value, traceback):
    '''Return terminal to blocking'''
    self.echo()
    # termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.oldterm)
    # fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
    return isinstance(value, TypeError)
  def getch(self):
    
    c = sys.stdin.read(1)
    if c == '\x1b':
      c += sys.stdin.read(2)
      # flush any data that has accumulated.
      # termios.tcflush(self.fd, termios.TCIOFLUSH)
      # flush just the input
      termios.tcflush(self.fd, termios.TCIFLUSH)
      
      # old flush method
      # while self.isData(): x = sys.stdin.read(1) 
    return c
    
    
  # def __enter__(self, type, value, traceback):
  #   '''Build it up for a with'''
  #   self.fd = sys.stdin.fileno()
  #   self.oldterm = termios.tcgetattr(self.fd)
  #   self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
  #   
  #   # Enables some nice bits for the terminal so that we can grab the charcers 
  #   # without blocking things
  #   newattr = termios.tcgetattr(self.fd)
  #   newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  #   termios.tcsetattr(self.fd, termios.TCSANOW, newattr)
  #   fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)
  #   return self
  # 
  # def __exit__(self, type, value, traceback):
  #   '''Tear everything down'''
  #   termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
  #   fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
  #   return isinstance(value, TypeError)
  # 
  # def getline(self):
  #   '''Attempts to gather a line'''
  #   while 1:
  #     try: 
  #       c = sys.stdin.read(10)
  #       break
  #     except IOError:
  #       pass
  #   return c


# Old getch example:
# def getch():
#   '''Get a character from the terminal.
#   Accepts escape sequences and also returns them.
#   This kills the cpu, try getchar.
#   I found this off of stackoverflow'''
#   fd = sys.stdin.fileno()
#   
#   # Enables some nice bits for the terminal so that we can grab the charcers 
#   # without blocking things and saving the old flags
#   oldterm = termios.tcgetattr(fd)
#   newattr = termios.tcgetattr(fd)
#   newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
#   termios.tcsetattr(fd, termios.TCSANOW, newattr)
#   
#   oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
#   fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
#   
#   try:        
#     while 1:            
#       try:
#         # Try to get at most 10 bytes of an escape sequence
#         c = sys.stdin.read(10)
#         break
#       except IOError: 
#         pass
#   finally:
#     termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
#     fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
#   return c
