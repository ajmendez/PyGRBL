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
  
  def gcode(self, method='G01'):
    return "%s X%6.4f Y%6.4f Z%6.4f"%(method, self.x, self.y, self.z)
  
  def save(self):
    v = (self.x, self.y, self.z)
    if len(self.previous) > self.maxpoints:
      self.pop(0)
    if len(self.previous) == 0 or self.previous[-1] != v:
      self.previous.append(v)





class GrblScreen(Screen):
  
  def hook_init(self):
    # self.screen.addstr(1,1,"This is my simple motion thing")
    self.G.write = self.history.write
    self.G.read = self.cmd.input
    self.state ='key'
    # self.G.run(self.G.HEADER)
    # self.history.refresh()
  
  def hook_key(self, key, mod):
    '''Returns true if got a key else false.'''
    if mod == 27: move = self.shiftmove
    else: move = self.move
    # Move Keys -- modifier for shift key ?!?!
    if   key == curses.KEY_UP    or (mod==27 and key== 67): self.location.relative(x= move)
    elif key == curses.KEY_DOWN  or (mod==27 and key== 68): self.location.relative(x=-move)
    elif key == curses.KEY_LEFT  or (mod==27 and key== 98): self.location.relative(y= move)
    elif key == curses.KEY_RIGHT or (mod==27 and key==102): self.location.relative(y=-move)
    elif key == ord('a') or key == ord('A'): self.location.relative(z= move)
    elif key == ord('z') or key == ord('Z'): self.location.relative(z=-move)
    # With Shift Key becomes large Moves
    else:
      # self.screen.addstr(2,1,'Pressed:(%s)(%s)'%(mod, key))
      return False
    return True
  def hook_update(self):
    '''If Keyfunction returns true, this is run'''
    # self.screen.addstr(2,1,"Location: %s"%(self.location))
    # self.history.write("Location: %s"%(self.location))
    self.cmd.run(self.location.gcode())
    # self.history.debug(self.location.gcode())
    self.history.refresh()
  
  def __init__(self):
    self.G = Grbl(self)
    self.version=0.1
    self.title='pyGrblScreen v%3.1f'%self.version
    
    self.location = ToolPath()
    self.move = 0.5
    self.shiftmove = 1.0
    
    Screen.__init__(self,title=self.title, version=self.version)

if __name__ == "__main__":
  s = GrblScreen()
