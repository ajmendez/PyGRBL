#!/usr/bin/env python
"""\
Simple g-code find the origin script
"""
import curses
from grbl import Grbl
from screen import Screen


class ToolPath(object):
  def __init__(self, x=0.0, y=0.0, z=0.0, maxpoints=10000):
    self.maxpoints = maxpoints
    self.x, self.y, self.z = x, y, z
    self.previous = []
    self.save()
  
  def absolute(self, x=None, y=None, z=None):
    if x: self.x = x
    if y: self.y = y 
    if z: self.z = z
    self.save()
  
  def relative(self, x=None, y=None, z=None):
    if x: self.x += x
    if y: self.y += y
    if z: self.z += z
    self.save()
  
  def __str__(self):
    return "%8.4f %8.4f %8.4f"%(self.x, self.y, self.z)
  
  def save(self):
    v = (self.x, self.y, self.z)
    if len(self.previous) > self.maxpoints:
      self.pop(0)
    if len(self.previous) == 0 or self.previous[-1] != v:
      self.previous.append(v)


class GrblScreen(Screen,Grbl):
  
  
  def move_key(self, key):
    '''Returns true if got a key else false.'''
    # Small Moves
    if   key == curses.KEY_UP:     self.location.relative(x= self.move)
    elif key == curses.KEY_DOWN:   self.location.relative(x=-self.move)
    elif key == curses.KEY_LEFT:   self.location.relative(y= self.move)
    elif key == curses.KEY_RIGHT:  self.location.relative(y=-self.move)
    elif key == ord('a'):          self.location.relative(z= self.move)
    elif key == ord('z'):          self.location.relative(z=-self.move)
    # With Shift Key becomes large Moves
    # elif key == curses.KEY_SUP:     self.location.relative(x= self.shiftmove)
    # elif key == curses.KEY_SDOWN:   self.location.relative(x=-self.shiftmove)
    elif key == curses.KEY_SLEFT:   self.location.relative(y= self.shiftmove)
    elif key == curses.KEY_SRIGHT:  self.location.relative(y=-self.shiftmove)
    elif key == ord('A'):           self.location.relative(z= self.shiftmove)
    elif key == ord('Z'):           self.location.relative(z=-self.shiftmove)
    else:
      self.screen.addstr(2,1,'Pressed:[%s]'%key)
      # self.screen.addstr(3,1,"Mouse: [%s]"%' '.join(self.screen.getmouse()))
      return False
    return True
  def move_update(self):
    '''If Keyfunction returns true, this is run'''
    self.screen.addstr(1,1,"Location: %s"%(self.location))
    
  def __init__(self):
    self.version=0.1
    self.title='pyGrblScreen v%3.1f'%self.version
    
    self.location = ToolPath()
    self.move = 0.5
    self.shiftmove = 1.0
    
    self.keyfunction = self.move_key
    self.update = self.move_update
    
    Grbl.__init__(self, debug=True)
    Screen.__init__(self,title=self.title, version=self.version, raw=True)
    
# try:
#   screen = curses.initscr()
#   curses.noecho()
#   curses.cbreak()
#   # screen.keypad(1)
#   # curses.raw()
#   screen.clear()
#   screen.border()
#   while 1:
#     # curses.raw()
#     # key = screen.getkey()
#     key = screen.getch()
#     if key == ord('q') or key == 'q':
#       break
#     if key == curses.KEY_MOUSE:
#       screen.addstr(1,1,'                                 ')
#       screen.addstr(2,1,'                                 ')
#       screen.addstr(1,1,'Got Mouse:[%s]'%', '.join(curses.getmouse()))
#     else:
#       if key == 27:
#         key2 = screen.getch()
#       else:
#         key2 = -1
#       # key2=''
#       # if key == '^[':
#       #   
#       # else:
#       #   key2=''
#       screen.addstr(1,1,'                                 ')
#       screen.addstr(2,1,'                                 ')
#       screen.addstr(1,1,'Pressed: (%s)(%s)'%(key,key2))
#       if key == int:
#         screen.addstr(2,1,'     : [%s]'%curses.keyname(key))
# finally:
#   curses.nocbreak()
#   screen.keypad(0)
#   curses.echo()
#   curses.noraw()
#   curses.endwin()
  

    
s = GrblScreen()

# s = Screen(keyfunction=keyfunction)
