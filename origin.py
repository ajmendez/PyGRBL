#!/usr/bin/env python
"""\
Simple g-code zeroing script
"""
from grbl import grbl, gdebug

DEBUG = gdebug()
g = grbl(debug=DEBUG)

g.origin()