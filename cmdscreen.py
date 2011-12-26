#!/usr/bin/env python
"""\
Simple Command window with keyboard hooks
"""
import curses
from grbl import Grbl
from screen import Screen
from toolpath import ToolPath

class CmdScreen(Screen):
  def getwritten(self, message):
    return message
  
  def hook_init(self):
    self.G.write = self.getwritten
    self.G.read = self.cmd.input
    self.cmd.hook_fcn = self.G.run
    self.cmd.run(self.G.HEADER)
    self.state = 'cmd'
    
  def hook_key(self, key, mod):
    '''Returns true if got a key else false.'''
    if mod == 27: move = self.location.shiftmove
    else: move = self.location.move
    if   key == curses.KEY_UP    or (mod==27 and key== 67): self.location.relative(x= move)
    elif key == curses.KEY_DOWN  or (mod==27 and key== 68): self.location.relative(x=-move)
    elif key == curses.KEY_LEFT  or (mod==27 and key== 98): self.location.relative(y= move)
    elif key == curses.KEY_RIGHT or (mod==27 and key==102): self.location.relative(y=-move)
    elif key == ord('a') or key == ord('A'): self.location.relative(z= move)
    elif key == ord('z') or key == ord('Z'): self.location.relative(z=-move)
    # With Shift Key becomes large Moves
    else:
      return False
    return True
  def hook_update(self):
    '''If Keyfunction returns true, this is run'''
    self.cmd.run(self.location.gcode())
    self.history.refresh()
  def hook_message(self):
    return " # [shift] + Arrow Keys/A+D for GCode Motion. q to return to CMD"


  def __init__(self,G=None):
    if not G: G = Grbl()
    self.G = G
    self.location = ToolPath()
    Screen.__init__(self,title=self.G.title, version=self.G.version)