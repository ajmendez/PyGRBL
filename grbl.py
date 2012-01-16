#!/usr/bin/env python
####################
## Mendez
## [2011.12.11]
####################
import serial, time, readline, sys, getopt, socket, datetime
import fakeserial

VERSION = 0.1
TITLE = 'pyGRBL v%3.1f'%(VERSION)
# Watching server
HOST, PORT = "localhost", 3225
HEADER = ''' ([%s] : header commands )
G20
G90
G00 X0Y0Z0
M03
G04 P3.000000
'''%(TITLE)

def gdebug(getargv=False):
  '''g(rbl)debug function, allows me to return either the debug bool/argv.'''
  DEBUG=False
  WATCH=False
  BASIC=False
  options,remainder = getopt.gnu_getopt(sys.argv[1:], 'dwb')
  for opt, arg in options:
    if opt == '-d': DEBUG=True
    if opt == '-w': WATCH=True
    if opt == '-b': BASIC=True
  if getargv:
    remainder.insert(0,sys.argv[0])
    return (DEBUG, WATCH, BASIC, remainder)
  return (DEBUG, WATCH, BASIC)



    


class Grbl:
  HEADER=HEADER
  
  def __init__(self, dev=None, speed=None, 
               debug=False, watch=False, basic=False, waittime=0.4):
    '''Starts the Serial/FakeSerial device'''
    if not dev: dev='/dev/tty.usbmodem1d11'
    if not speed: speed=9600
    self.waittime = waittime
    self.version = VERSION
    self.title = TITLE
    self.starttime = datetime.datetime.now()
    self.debug, self.watch, self.basic, self.argv = gdebug(getargv=True)
    if debug: self.debug = debug
    if watch: self.watch = watch
    if basic: self.basic = basic
    # self.debug = debug
    # self.watch = watch
    
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
        tmp = self.read("Could not connect to server. Press [Enter] to continue.")
        self.watch = False
        self.sock.close()
  
  def read(self, message):
    '''By Default just get input'''
    return raw_input(message)
  
  def write(self, message):
    '''By default output to the screen.'''
    print message
  
  def quit(self):
    '''Shuts down the system'''
    self.s.close()
    if self.watch:
      self.sock.close()
  
  def run(self, cmd, echocmd=False, cmdprefix='Sending'):
    '''Run a command: '''
    if echocmd:
      self.write( '%s: %s'%(cmdprefix,cmd) )
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
      return self.write('\n'.join([' |  ' + o for o in out.splitlines()]))
    return 'Nothing returned'
  
  def timeleft(self,i,total,totaltime=False):
    '''From the current step, and total steps, estimate the time left'''
    if i == 0: return "Unknown"
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
      self.progress, self.time = p/100.0,t
      self.run(l, echocmd=True, cmdprefix='[%2d%%][%s]Sending'%(p,t))
      
    
    # Wait here until grbl is finished to close serial port and file.
    self.write("!! %s ran for %s"%(self.title,
                           self.timeleft(len(lines),len(lines),totaltime=True)))
    self.read("   >>>  Press <Enter> to finish  <<<")
    
    