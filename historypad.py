#!/usr/bin/env python
# historypad.py
# [SUPPORT] -- Provide basic historypad curses window.
# [2012.01.31] Mendez

import curses

class HistoryPad(object):
  def __init__(self, height, width, y, x, maxlength=10000):
    self.height, self.width = height, width
    self.window = curses.newwin(height,width,y,x)
    self.history = []
    
    self.maxlength = maxlength
    self.wy, self.wx = 0,1
    self.linenum=0 # the line that we are on
  
  def write(self, message, attr=curses.A_NORMAL):
    for item in message.splitlines():
      if len(self.history) > self.maxlength:
        self.history.pop(0)
        self.linenum -= 1
      self.history.append( (item,attr) )
      
      if self.linenum > len(self.history)-2 or self.linenum == 0:
        self.linenum += 1
    
  def debug(window, message):
    height,width = window.getmaxyx()
    y,x = window.getyx()
    window.addstr(1,width-10," "*10)
    window.addstr(1,width-10,message)
    window.move(y,x)
    window.refresh()
  
  def refresh(self):
    y,x = self.window.getyx()
    iScreen = 0
    while len(self.history) < self.height - iScreen:
      iScreen += 1
    for i, item in enumerate(self.history):
      line, attr = item
      l = "%3d %s"%(i,line)
      if len(l) > self.width: l = l[0:self.width-1]
      # if i > self.linenum-self.height-iScreen and i <= self.linenum:
      if ( iScreen <= self.height and 
           i >= self.linenum-self.height and 
           i < self.linenum ):
        try: # this try can be removed was testing
          self.window.hline(self.wy+iScreen, self.wx, ' ', self.width-self.wx)
          self.window.addstr(self.wy+iScreen, self.wx, l, attr)
        except:
          self.window.addstr(1,1,"%d,%d,%s"%(self.wy+iScreen, self.wx, l),
                            curses.color_pair(2))
        iScreen += 1
    # self.window.move(y,x)
    self.window.refresh()
  
  def temp(self):
    item,attr = self.history.pop()
    item = "TEMP DEBUG(%d, %d)"%(self.linenum, self.height)
    self.history.append((item,attr))
  
  
  def pageup(self):
    self.linenum -= self.height
    if self.linenum < 0: self.linenum = 0
    if len(self.history) - self.height < self.linenum:
      self.linenum = self.height+1
    self.temp()
    self.refresh()
  def pagedown(self):
    self.linenum += self.height
    if self.linenum > len(self.history): self.linenum = len(self.history)
    self.temp()
    self.refresh()
  def clear(self):
    self.linenum=0
    self.history = []
    self.window.clear()
    self.refresh()
