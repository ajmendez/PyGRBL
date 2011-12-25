#!/usr/bin/env python
####################
## Mendez
## [2011.12.11]
####################
import serial, time, readline, sys, getopt, curses, socket, datetime
import fakeserial

# Watching server
HOST, PORT = "localhost", 3225


def gdebug(getargv=False):
  '''g(rbl)debug function, allows me to return either the debug bool/argv.'''
  DEBUG=False
  WATCH=False
  options,remainder = getopt.gnu_getopt(sys.argv[1:], 'dw')
  for opt, arg in options:
    if opt == '-d':
      DEBUG=True
    if opt == '-w':
      WATCH=True
  if getargv:
    remainder.insert(0,sys.argv[0])
    return (DEBUG, WATCH, remainder)
  return (DEBUG, WATCH)


class Screen(object):
  def __init__(self, version=None, title=None, raw=False):
    '''initalize a curses screen using the wrapper'''
    if not version: version=0.1
    if not title: title='pyScreen v%3.1f'%(version)
    self.version = version
    self.title = title
    self.raw = raw
    curses.wrapper(self.begin)
  
  def begin(self, screen):
    '''Get some basic values and start the main loop'''
    self.screen = screen
    self.height, self.width = screen.getmaxyx()
    self.offsety, self.offsetx = -self.height / 2, -self.width / 2
    self.make_title(clear=True)
    if self.raw: 
      self.screen.addstr(3,1,'RAW')
      curses.raw()


    self.main()
  
  def update(self):
    pass
  
  def main(self):
    keyfunction = self.keyfunction
    while 1:
      key = self.screen.getch()
      if self.key_exit(key): pass
      elif hasattr(self,'keyfunction') & self.keyfunction(key): self.update()
      elif key == ord('t'): self.make_title(title='test')
      
  
  def key_exit(self,key):
    if (key == curses.KEY_EXIT or
        key == curses.KEY_SEXIT or
        key == curses.KEY_CANCEL or 
        key == ord('q')):
      sys.exit()
  
  def make_title(self,title=None, clear=False):
    '''Clears the window and setups a title'''
    if not title: title = self.title
    if clear:
      self.screen.clear()
      self.screen.border()
    else:
      self.screen.hline(0,1,curses.ACS_HLINE,self.width-2)
    self.screen.addstr(0,2,'[%s]'%(title))
    self.screen.refresh()
    


class Grbl:
  def __init__(self, dev=None, speed=None, debug=False, watch=False, waittime=0.5):
    '''Starts the Serial/FakeSerial device'''
    if not dev: dev='/dev/tty.usbmodem1d11'
    if not speed: speed=9600
    self.waittime = waittime
    self.version = 0.1
    self.title = 'pyGRBL v%3.1f'%(self.version)
    self.starttime = datetime.datetime.now()
    self.debug = debug
    self.watch = watch
    
    # Start the serial port
    if self.debug:
      self.waittime=0.05
      self.s = fakeserial.Serial()
    else:
      self.s = serial.Serial(dev,speed)
      self.s.open()
      self.s.isOpen()
      # Wake up grbl
      self.s.write("\r\n\r\n")
      time.sleep(1)   # Wait for grbl to initialize
      self.s.flushInput()  # Flush startup text in serial input
    
    if self.watch:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
        self.sock.connect((HOST, PORT))
        self.sock.send("(Connection Test)")
      except:
        tmp = raw_input("Could not connect to server. Press [Enter] to continue.")
        self.watch = False
        self.sock.close()
  
  def write(self, message):
    '''if we are using a nice litle curses app, lets figure this out.'''
    if not self.scr:
      print message
    else:
      pass
  
  def quit(self):
    '''Shuts down the system'''
    self.s.close()
    if self.watch:
      self.sock.close()


    
  def origin(self):
    '''Make sure to start with everything zeroed out.'''
    self.screen()
    cmd=raw_input()
    self.quit()
  
  
  def run(self, cmd, echocmd=False, cmdprefix='Sending'):
    '''Run a command: '''
    if echocmd:
      print '%s: %s'%(cmdprefix,cmd)
    self.s.write(cmd+'\n')
    if self.watch:
      try:
        self.sock.send(cmd+'\n')
      except:
        tmp = raw_input("Watch Server Gone. Press [Enter] to continue.")
        self.watch = False
      
    out=''
    time.sleep(self.waittime)
    while self.s.inWaiting() > 0:
      out += self.s.read(1)
    if out != '':
      print '\n'.join([' |  ' + o for o in out.splitlines()])
  
  def timeleft(self,i,total,totaltime=False):
    '''From the current step, and total steps, estimate the time left'''
    if i == 0:
      return "Unknown"
    # there has to be a better way
    delta = (datetime.datetime.now() - self.starttime)
    timeleft = (total-i)/float(i)*delta.total_seconds()
    if totaltime:
      timeleft = delta.total_seconds()
    
    if timeleft < 60:
      return "%d sec"%(timeleft)
    elif (timeleft/60.) < 60:
      return "%3.1f min"%(timeleft/60.)
    elif (timeleft/3600.) < 24:
      return "%3.1f hr"%(timeleft/3600.)
    else:
      return "%d days!!!"%(timeleft/(3600*24.))
    
  
  def runfile(self, gfile=None):
    '''Run a specific G-code file'''
    f = open(gfile,'r')
    lines = f.readlines()
    f.close()
    for i,line in enumerate(lines):
      l = line.strip() # Strip all EOL characters for streaming
      p = i/float(len(lines))*100
      t = self.timeleft(i,len(lines))
      self.run(l, echocmd=True, cmdprefix='[%2d%%][%s]Sending'%(p,t))
    
    # Wait here until grbl is finished to close serial port and file.
    print "%s ran for %s"%(self.title,
                           self.timeleft(len(lines),len(lines),totaltime=True))
    raw_input(">>>  Press <Enter> to finish  <<<")
    
    