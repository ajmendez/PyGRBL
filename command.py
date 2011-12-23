#!/usr/bin/env python
"""\
Simple g-code debuging tool
"""
from grbl import Grbl, gdebug
DEBUG,WATCH = gdebug()

g = Grbl(debug=DEBUG, watch=WATCH)

while True:
    x = raw_input('cmd> ')
    if x.strip() == 'quit' or x.strip() == 'exit':
      g.quit()
      exit()
    else:
      g.run(x)