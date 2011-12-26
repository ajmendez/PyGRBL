import curses, sys, time, readline, re 
import curses.textpad, curses.ascii
from historypad import HistoryPad
from cmdline import CmdLine

HELP='''!! some extra value from Mendez
help        -- This listing of not so helpful things.
key/k       -- Move the mill using the keyboard.
exit/quit/q -- Close the program.
error       -- display an error message
clear       -- clear the screen.
'''

class Screen(object):
  def __init__(self, version=None, title=None):
    '''initalize a curses screen using the wrapper'''
    if not version: version=0.1
    if not title: title='pyScreen v%3.1f'%(version)
    self.version = version
    self.title = title
    self.help = HELP
    self.cmdheight=1
    self.padlength=10000
    self.state = 'key' # or 'cmd' or 'exit'
    curses.wrapper(self.begin)
    
  def begin(self, screen):
    '''Get some basic values and start the main loop'''
    self.screen = screen
    curses.init_pair(1,curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_BLUE, curses.COLOR_BLACK)
    self.height, self.width = screen.getmaxyx()
    self.make_title(clear=True)
    self.make_default()
    self.main()
  
  def message(self, message, debug=False):
    if debug: wy,wx = self.height/2, self.width/2
    else:     wy,wx = 1,1
      
      
    if hasattr(self,'history') and not debug:
      self.history.write(message, attr=curses.color__pair(2))
    else:
      y,x = self.screen.getyx()
      self.screen.hline(wy,wx,' ',self.width-2-wy)
      self.screen.addstr(wy,wx,message)
      time.sleep(0.4)
      self.screen.move(y,x)
      
  def hook_init(self):
    self.message("Example hook_init function")
  def hook_update(self):
    self.message("Example hook_key/hood_update function")
  def hood_key(self,key,mod):
    self.message("Pressed Key :(%s)(%s)"%(key,mod))
    if key =='h' or key == ord('h'):
      return True # Press h to see an example
    return False
  
  
  def get_key(self):
    # Get a key / modifier pair:
    key = self.screen.getch()
    mod = -1
    if key == 27 or key == '^[':
      mod = key
      key = self.screen.getch()
    return key,mod
  
  def main_keypress(self):
    while 1:
      key, mod = self.get_key()
      if self.key_exit(key): break ## lets always be able to exit
      elif hasattr(self, 'hook_key') and self.hook_key(key, mod): self.hook_update()
      elif self.key_default(key, mod): pass
      elif key == ord('t'): self.make_title(title='test')
  
  def main_command(self):
    while 1:
      cmd = self.cmd.input()
      if cmd == 'quit' or cmd == 'exit' or cmd == 'q': 
        self.state='exit'
        break
      elif cmd == 'clear': self.history.clear()
      elif cmd == 'error': self.message('ERROR!', debug=True)
      elif cmd == 'help': self.cmd.echo(self.help)
      elif cmd == 'key' or cmd == 'k': 
        self.state = 'key'
        self.cmd.info = self.hook_message()
        break
      elif '$' in cmd or 'G' in cmd:
        self.cmd.run(cmd)
      else:
        if len(cmd) > 0: cmd ='!! %s'%cmd
        self.cmd.run(cmd)
  
  def refresh(self):
    self.cmd.state = self.state
    self.screen.refresh()
    self.cmd.refresh()
    self.history.refresh()
  
  def main(self):
    if hasattr(self, 'hook_init'):
      self.hook_init()
    while 1:
      self.refresh()
      if self.state == 'key': self.main_keypress()
      elif self.state == 'cmd': self.main_command()
      else: break
  
  def key_exit(self,key):
    if (key == curses.KEY_EXIT or
        key == curses.KEY_SEXIT or
        key == curses.KEY_CANCEL or 
        key == ord('q') or
        key == ord('Q') ):
      if self.state == 'key':
        self.state='cmd'
        self.cmd.info=self.cmd.prompt
        return True
    else:
      return False
  
  def key_default(self,key,mod):
    #PPAGE and NPAGE are being theieved by terminal
    if   key == curses.KEY_PPAGE or key == ord('j'): self.history.pageup()
    elif key == curses.KEY_NPAGE or key == ord('k'): self.history.pagedown()
    else: return False
    return True
  
  
  
  def make_title(self,title=None, clear=False):
    '''Clears the window and setups a title'''
    if not title: title = self.title
    if clear:
      self.screen.clear()
      self.screen.border()
    else:
      self.screen.hline(0,1,curses.ACS_HLINE,self.width-2)
    self.screen.addstr(0,2,'[%s]'%(title))
  
    
  def make_default(self):
    '''Makes the default history pad and command pad'''
    self.history = HistoryPad(self.height-3-self.cmdheight, self.width-2,1,1)
    self.history.write('%s Started'%(self.title))
    self.cmd = CmdLine(self.cmdheight+2, self.width, 
                          self.height-self.cmdheight-2, 0,
                          history=self.history)








## debug function
if __name__ == '__main__':
  try:
    screen = curses.initscr()
    height,width = screen.getmaxyx()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)
    curses.raw()
    screen.clear()
    screen.border()
    
    ##### key processing
    while 1:
      key = screen.getch()
      key2 = -1
      if key == ord('q') or key == 'q': # to switch to getkey
        break
      else:
        if key == 27:
          key2 = key
          key = screen.getch()
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