import curses

class CmdLine(object):
  def __init__(self,height, width, y, x, state='cmd',history=None):
    self.height, self.width = height, width
    self.window = curses.newwin(height,width,y,x)
    self.window.border(0,0,0,0,curses.ACS_SSSB,curses.ACS_SBSS)
    self.state=state
    self.wy, self.wx = 1, 5
    self.textwin = self.window.subwin(height-2, width-self.wx, y+self.wy, x+self.wx)
    self.history = history
    self.prompt = ' >  '
    self.info = self.prompt
  
  def refresh(self):
    '''This updates the title depending on the mode that we are under'''
    self.window.addstr(0,1,' %s '%self.state.upper())
    self.window.addstr(1,1, self.info)
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
    valueattr = curses.color_pair(3)
    if hasattr(self, 'hook_fcn'):
      value = self.hook_fcn(cmd)
      self.history.write(value, attr=valueattr)
    else:
      cmd = "Not Hooked : "+cmd
    self.echo(cmd)
  
  def echo(self, cmd):
    if '!!' in cmd: attr = curses.color_pair(2)
    else: attr = curses.color_pair(1)
    self.history.write(cmd, attr=attr)
    self.history.refresh()
  
  def input(self):
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