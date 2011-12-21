#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
"""

from grbl import grbl, gdebug
DEBUG,argv = gdebug(getargv=True)
g = grbl(debug=DEBUG)
g.run('$') # Print out the current settings

print "%s is opening %s"%(argv[0],argv[1])
g.runfile(argv[1])
