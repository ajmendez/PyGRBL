#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
"""

# from grbl import Grbl, gdebug
# DEBUG,WATCH,argv = gdebug(getargv=True)
# g = Grbl(debug=DEBUG,watch=WATCH)
from grbl import Grbl
g = Grbl()
g.run('$') # Print out the current settings

print "%s is opening %s"%(g.argv[0],g.argv[1])
g.runfile(g.argv[1])
