#!/usr/bin/env python
# point.py :: a nice named tuple named point for all of my point needs
#             we allways seem to need one of these objects
# [2012.08.28] -- Mendez 

from collections import namedtuple
from rcdtype import *

_name = 'point'
_defaults = ('x','y','z')
_extra = ('cmd','index') # comes after defaults
_nan = float('nan')
PT = recordtype(_name, ' '.join(_defaults + _extra) )

class Point(PT):
  def __init__(self, *args, **kwargs):
    # set default to be nan
    for x in _defaults:
      if not x in kwargs:
        kwargs[x] = _nan
    for x in _extra:
      if not x in kwargs:
        kwargs[x] = -1
    # super(Point, self).__init__(*args, **kwargs)
    PT.__init__(self, *args, **kwargs)
  def __getitem__(self,key):
    if isinstance(key,str):
      print key, _defaults.index(key)
      return -1 
      # return self[_defaults.index(key)]
    else:
      return PT.__getitem__(self,key)


if __name__ == "__main__":
  p = Point()
  print p
  p.x = 0

  print 'X : '
  print p.x, p[0], p['x']

  print 'Slice: '
  print p[0:3], p[0:10]
