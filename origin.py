#!/usr/bin/env python
"""\
Simple g-code find the origin script
"""
from grbl import Grbl, gdebug

DEBUG = gdebug()
g = Grbl(debug=DEBUG)

g.origin()