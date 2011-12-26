#!/usr/bin/env python
"""\
Simple g-code find the origin script
"""
from cmdscreen import CmdScreen

class GrblScreen(CmdScreen):
  def hook_init(self):
    CmdScreen.hook_init(self)
    # switch over to the key interface
    self.state = 'key'
    self.cmd.info = self.hook_message()

if __name__ == "__main__":
  s = GrblScreen()
