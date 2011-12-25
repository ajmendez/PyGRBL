import curses, sys, time, readline, re 
import curses.textpad, curses.ascii

class Screen(object):
  def __init__(self, version=None, title=None, raw=False, nodefault=False):
    '''initalize a curses screen using the wrapper'''
    if not version: version=0.1
    if not title: title='pyScreen v%3.1f'%(version)
    self.version = version
    self.title = title
    self.raw = raw
    self.nodefault = nodefault
    self.cmdheight=1
    self.padlength=10000
    self.state = 'key' # or 'cmd'
    curses.wrapper(self.begin)
  
  def begin(self, screen):
    '''Get some basic values and start the main loop'''
    self.screen = screen
    self.height, self.width = screen.getmaxyx()
    self.make_title(clear=True)
    self.make_default()
    # if self.raw:
    #   self.screen.keypad(1)
    #   curses.raw()
    self.main()
  
  def hook_init(self):
    self.screen.addstr(self.height-3,1,"Example hook_init function")
  def hook_update(self):
    self.screen.addstr(self.height-2,1,"Example hook_key/hood_update function")
  def hood_key(self,key,mod):
    self.screen.addstr(self.height-2,1,"Pressed Key :(%s)(%s)"%(key,mod))
    if key =='h' or key == ord('h'):
      return True
    return False
  
  def main_keypress(self):
    while 1:
      # Get a key / modifier pair:
      key = self.screen.getch()
      mod = -1
      if key == 27 or key == '^[':
        mod = key
        key = self.screen.getch()
      
      
      if self.key_exit(key): pass ## lets always be able to exit
      elif self.hook_key(key, mod): self.hook_update()
      elif self.key_default(key, mod): pass
      elif key == ord('t'): self.make_title(title='test')
  
  def main_command(self):
    if self.nodefault or (not hasattr(self,'cmd')): return
    
    while 1:
      cmd = self.cmd.input()
      if cmd == 'quit' or cmd == 'exit': break
      elif cmd == 'clear': self.history.clear()
      elif cmd == 'manual': 
        self.state = 'key'
        break
      else:
        # self.history.debug('running')
        self.cmd.run(cmd)
  
  def main(self):
    if hasattr(self, 'hook_init'):
      self.hook_init()
    while 1:
      if self.state == 'key':
        self.main_keypress()
      elif self.state == 'cmd':
        self.main_command()
      else:
        break
  
  def key_exit(self,key):
    if (key == curses.KEY_EXIT or
        key == curses.KEY_SEXIT or
        key == curses.KEY_CANCEL or 
        key == ord('q') or
        key == ord('Q') ):
      if self.state == 'key':
        self.state='cmd'
  
  def key_default(self,key,mod):
    if self.nodefault or (not hasattr(self,'history')): return False
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
    self.screen.refresh()
  
    
  def make_default(self):
    '''Makes the default history pad and command pad'''
    if self.nodefault: return
    
    
    self.history = HistoryPad(self.height-3-self.cmdheight, self.width-2,1,1)
    self.history.write('%s Started'%(self.title))
    self.history.refresh()
    
    self.cmd = CmdPad(self.cmdheight+2, self.width, 
                          self.height-self.cmdheight-2, 0,
                          history=self.history)
    self.cmd.refresh()









class CmdPad(object):
  def __init__(self,height, width, y, x, history=None):
    self.height, self.width = height, width
    self.window = curses.newwin(height,width,y,x)
    self.window.border(0,0,0,0,curses.ACS_SSSB,curses.ACS_SBSS)
    self.window.addstr(0,1,"CMD")
    self.window.addstr(1,1," >")
    self.wy, self.wx = 1, 5
    self.textwin = self.window.subwin(height-2, width-self.wx, y+self.wy, x+self.wx)
    self.history = history
  def refresh(self):
    self.window.refresh()
    # self.textwin.refresh()
  
  def validator(self, c):
    if c == curses.ascii.NL or c == curses.ascii.CR:
      return curses.ascii.BEL
    elif c == curses.ascii.BS:
      return curses.erasechar()
    else:
      return c
  
  def run(self, cmd):
    if hasattr(self, 'hook_fcn'):
      self.hook_fcn(cmd)
    else:
      cmd = "Not Hooked : "+cmd
      # cmd = 'NOT RUNNING: '+cmd
    self.history.write(cmd)
    self.history.refresh()
  
  def input(self):
    # txtwin = curses.newwin(self.height-2, self.width-self.wx, self.wy, self.wx)
    # self.textwin.clrtoeol()
    self.textwin.hline(0,0,' ' ,self.width)
    box = curses.textpad.Textbox(self.textwin)
    text = box.edit(self.validator)
    # curses.nocbreak()
    # curses.echo()
    # curses.noraw()
    # text = raw_input()
    # curses.noecho()
    # curses.cbreak()
    # curses.raw()
    # self.textwin.clrtoeol()
    # self.history.debug(text)
    return text.strip()
    
    # pad = curses.textpad.Textbox(self.window)
    # self.debug
    # if 'end' in pad.gather():
    #   return pad.gather()
      
    
    
    
    








class HistoryPad(object):
  def __init__(self, height, width, y, x, maxlength=10000):
    self.height, self.width = height, width
    self.window = curses.newwin(height,width,y,x)
    self.history = []
    self.maxlength = maxlength
    self.wy, self.wx = 0,1
    self.linenum=0 # the line that we are on
  
  def write(self, message):
    # print message
    if len(self.history) > self.maxlength:
      self.history.pop(0)
      self.linenum -= 1
    self.history.append(message)
    # follow updates if at the end
    if self.linenum > len(self.history)-2 or self.linenum == 0:
      self.linenum += 1
  
  def debug(self, message):
    y,x = self.window.getyx()
    self.window.addstr(1,self.width-10," "*10)
    self.window.addstr(1,self.width-10,message)
    self.window.move(y,x)
    self.window.refresh()
  
  def refresh(self):
    y,x = self.window.getyx()
    iScreen = 0
    while len(self.history) < self.height - iScreen:
      iScreen += 1
    for i, line in enumerate(self.history):
      l = "%d %s"%(i,line)
      if len(l) > self.width:
        l = l[0:self.width-1]
      if i >= self.linenum-self.height-iScreen and i <= self.linenum:
        self.window.hline(self.wy+iScreen, self.wx, ' ', self.width-self.wx)
        # self.window.clrtoeol()
        self.window.addstr(self.wy+iScreen, self.wx, l)
        iScreen += 1
    self.window.move(y,x)
    self.window.refresh()
  
  def pageup(self):
    self.linenum -= self.height
    if self.linenum < 0:
      self.linenum = 0
    if len(self.history) - self.linenum < self.height:
      self.linenum = len(self.history)
    self.update()
  def pagedown(self):
    self.linenum += self.height
    if self.linenum > len(self.history):
      self.linenum = len(self.history)
    self.update()
  def clear(self):
    self.linenum=0
    self.history = []
    self.window.clear()
    self.refresh()
    









## debug function
if __name__ == '__main__':
  try:
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    # screen.keypad(1)
    # curses.raw()
    screen.clear()
    screen.border()
    while 1:
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