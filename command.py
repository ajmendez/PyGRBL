#!/usr/bin/env python
"""\
Simple g-code debuging tool
"""
from grbl import Grbl
from commandscreen import CommandScreen

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
    s = CommandScreen(G)