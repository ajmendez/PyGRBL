#!/usr/bin/env python
"""\
Simple g-code debuging tool
"""

from grbl import Grbl
from screen import Screen
# from grbl import Grbl, gdebug
# DEBUG,WATCH = gdebug()

# g = Grbl(debug=DEBUG, watch=WATCH)




# g = Grbl()
# 
# while True:
#     x = raw_input('cmd> ')
#     if x.strip() == 'quit' or x.strip() == 'exit':
#       g.quit()
#       exit()
#     else:
#       g.run(x)


class CommandScreen(Screen):
  def hook_init(self):
    self.G.write = self.history.write
    self.G.read = self.cmd.input
    self.cmd.hook_fcn = self.G.run
    self.G.run(self.G.HEADER)
    # self.history.window.refresh()
    self.state = 'cmd'
  def __init__(self):
    self.G = Grbl(self)
    Screen.__init__(self,title=self.G.title, version=self.G.version)
    
    
s = CommandScreen()