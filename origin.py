#!/usr/bin/env python
# origin.py
# A quick origin finding script
#  python origin.py [-d][-w]
# [2012.01.31] Mendez

from cmdscreen import CmdScreen

class GrblScreen(CmdScreen):
  def hook_init(self):
    CmdScreen.hook_init(self)
    # switch over to the key interface
    self.state = 'key'
    self.cmd.info = self.hook_message()

if __name__ == "__main__":
  s = GrblScreen()
