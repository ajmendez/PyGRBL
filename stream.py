#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
"""

from grbl import Grbl, gdebug
DEBUG,WATCH,argv = gdebug(getargv=True)
g = Grbl(debug=DEBUG,watch=WATCH)
g.run('$') # Print out the current settings

print "%s is opening %s"%(argv[0],argv[1])
g.runfile(argv[1])
