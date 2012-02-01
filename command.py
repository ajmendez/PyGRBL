#!/usr/bin/env python
# command.py
# Either runs a basic command screen or a full curses screen.
#    python command.py -b         Basic gcode entry method
#    python command.py -d         DEBUG with fake serial
#    python command.py -w         Enable Watch
# [2012.01.31] Mendez

from grbl import Grbl
from cmdscreen import CmdScreen

if __name__ == "__main__":
  G = Grbl()
  if G.basic:
    while True:
      x = raw_input('cmd> ')
      if x.strip() == 'quit' or x.strip() == 'exit':
        G.quit()
        break
      else:
        G.run(x)
  else:
    s = CmdScreen(G)