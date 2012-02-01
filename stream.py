#!/usr/bin/env python
# stream.py
# Stream a gcode file
#  python stream.py -b file.nc          Basic stream
#  python stream.py file.nc             Curses window stream
#  python stream.py -d file.nc          Enable DEBUG fakeserial
#  python stream.py -w file.nc          Enable watch server
# [2012.01.31] Mendez

import curses
from cmdscreen import CmdScreen
from grbl import Grbl


class GrblScreen(CmdScreen):
  def historywrite(self,message):
    '''I am not sure if there is something wrong here, but it works.'''
    if 'Sending' in message: attr = curses.color_pair(1)
    else: attr = 0
    self.history.write(message, attr=attr)
    self.state='run'
    self.cmd.info=" Running file: %s"%(self.G.argv[1])
    self.cmd.progressbar(self.G.progress)
    self.cmd.updatetime('[%s]'%self.G.time)
    self.refresh()
    # self.history.refresh()
  
  def hook_init(self):
    CmdScreen.hook_init(self)
    self.G.write = self.historywrite
    # switch over to the key interface
    # help(self.G.write)
    self.G.runfile(self.G.argv[1])

if __name__ == "__main__":
  G = Grbl()
  if G.basic:
    G.write("%s is opening %s"%(G.argv[0],G.argv[1]))
    G.run('$') # Print out the current settings
    G.runfile(G.argv[1])
  else:
    s = GrblScreen(G)