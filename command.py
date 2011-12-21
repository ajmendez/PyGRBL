#!/usr/bin/env python
"""\
Simple g-code debuging tool
"""
from grbl import grbl, gdebug
DEBUG = gdebug()

g = grbl(debug=DEBUG)

while True:
    x = raw_input('cmd> ')
    if x.strip() == 'quit' or x.strip() == 'exit':
      g.quit()
      exit()
    else:
      g.run(x)