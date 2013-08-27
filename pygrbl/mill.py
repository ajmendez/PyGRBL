#!/usr/bin/env python
# mill.py : Parses a gcode file
# [2012.08.01] Mendez
# from collections import deque
from itertools import cycle
from util import distance, uniqify
NPRINT = 5
EPSILON = 2 # mil [2] distance seperating start and end locations for loop

class Mill(list):
  def __repr__(self):
    n = NPRINT if NPRINT < len(self) else len(self)
    return ('<%s toolpath[%s] : n=%i closed=%s drill=%s>%s ...'%(
              self.__class__.__name__,
              id(self),
              len(self),
              self.isClosed(),
              self.isDrill(),
              ''.join(['\n | %s, '%(str(x)) for x in self[0:n]]) ) )
  
  
  def length(self):
    '''Calculate the length in inches of this mill path'''
    length = 0.0
    for i in range(len(self)-1):
      length += distance(self[i],self[i+1])
    return length
  
  def center(self):
    '''calculate the center of mass of an mill.'''
    pass
  
  def uniqify(self):
    '''Removes points EXACTLY equal to a prevous point.'''
    for i in reversed(range(len(self)-1)):
      if self[i] == self[i+1]:
        self.pop(i+1)
    # new = uniqify(self)
  
  def setZ(self,z):
    for x in self:
      x[2] = z
  
  def closestIndex(self,X):
    ''' sort the mill to be close to vector X'''
    distances = [distance(point,X) for point in self]
    return distances.index(min(distances))
  
  def closestLocation(self,X):
    '''Get the location closest to X'''
    return self[self.closestIndex(X)]

  def reorderLocations(self, X):
    '''[SLOW] Reorder the mill to be close to X.  Only do this if the path is closed.
    Originally I had this as a deque object but that was stupid becuase it caused so many problems with slices'''
    if self.isClosed():
      index = self.closestIndex(X)
      for i in range(index+1): self.append(self.pop(0)) 
      self.append(self[0])
      
  
  def isClosed(self):
    '''Checks to see if the first and last point are close in space, so we assume that it is closed'''
    delta = distance(self[0],self[-1])
    return delta < EPSILON/1000.
  
  def isDrill(self):
    '''Check to see if this is a drill mill path, so length == 2(down, up), or length==1 (drilling location)'''
    return len(self) <= 2
    