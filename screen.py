import curses,sys

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
    self.main()
  
  def update(self):
    pass
  
  def main(self):
    keyfunction = self.keyfunction
    if self.raw: 
      self.screen.addstr(3,1,'RAW')
      self.screen.keypad(0)
      curses.nocbreak()
      curses.raw()
    
    while 1:
      key = self.screen.getch()
      key2=-1
      key3=-1
      if key == 27 or key == '^[':
        key2=key
        key=self.screen.getch()
      
      
      self.screen.addstr(4,4,"(%s)(%s)(%s)"%(key,key2,key3))
      if self.key_exit(key): pass ## lets always be able to exit
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
    

## debug function
try:
  screen = curses.initscr()
  curses.noecho()
  curses.cbreak()
  # screen.keypad(1)
  # curses.raw()
  screen.clear()
  screen.border()
  while 1:
    # curses.raw()
    # key = screen.getkey()
    key = screen.getch()
    if key == ord('q') or key == 'q':
      break
    if key == curses.KEY_MOUSE:
      screen.addstr(1,1,'                                 ')
      screen.addstr(2,1,'                                 ')
      screen.addstr(1,1,'Got Mouse:[%s]'%', '.join(curses.getmouse()))
    else:
      if key == 27:
        key2 = screen.getch()
      else:
        key2 = -1
      # key2=''
      # if key == '^[':
      #   
      # else:
      #   key2=''
      screen.addstr(1,1,'                                 ')
      screen.addstr(2,1,'                                 ')
      screen.addstr(1,1,'Pressed: (%s)(%s)'%(key,key2))
      if key == int:
        screen.addstr(2,1,'     : [%s]'%curses.keyname(key))
finally:
  curses.nocbreak()
  screen.keypad(0)
  curses.echo()
  curses.noraw()
  curses.endwin()