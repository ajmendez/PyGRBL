#!/usr/bin/env python
# util.py : some nice things
# [2012.07.30] - Mendez
import sys
from datetime import datetime
from math import sqrt
from clint.textui import colored, puts, indent
from copy import deepcopy

def error(message):
  '''Nice little error message for the user that causes a quit'''
  puts(colored.red('\n !!! '+message))
  sys.exit(1)



def deltaTime(start):
  '''From a start datetime object get a nice string of 'x hours, y minutes, z seconds'
  of time passed since the start. '''
  diff = datetime.now() - start
  # seconds = diff.seconds # limited to 1 second, so lets get fractions
  seconds = diff.days*86400 + diff.seconds + diff.microseconds/float(10**6)
  out = []
  epocs = [ [3600,'hour'],
            [60,'minute'],
            [1,'second'],
            [0.001,'milisecond'] ]
  factors,tmp = zip(*epocs)
  while seconds > min(factors):
    for factor, noun in epocs:
      if seconds >= factor:
        delta = seconds/factor
        if delta > 1: noun +='s'
        out.append('%d %s'%(delta,noun))
        seconds -= factor*(delta)
  
  return ', '.join(out)


def distance(A,B):
  '''euclidean distance of two lists. TODO should be generalized...
  IndexDict returns the 'x','y','z' strings for each of the axes so do it slighly diff'''
  a = A.values() if isinstance(A,IndexDict) else A
  b = B.values() if isinstance(B,IndexDict) else B
  return sqrt(sum([pow(alpha-beta,2) for alpha,beta in zip(a,b)]))


def uniqify(seq, idfun=None): 
   '''order preserving uniq function'''
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


def convertUnits(x,unit):
  '''Converts x into inches depending on unit'''
  tmp =( ('mm',1.0/25.4),
         ('inch',1.0),
         ('in',1.0),
         ('mil',1.0/1000.0) )
  units, scales = zip(*tmp)
  if not unit in units:
    error('Failed to convert Unit[%s] with known unit conversion: %s'%(unit,','.join(units)))
  return float(x)*scales[units.index(unit)]


def memorize(function):
  ''' A simple cache'''
  memo = {}
  def wrapper(*args):
    if args in memo:
      print "returning %s from cache" % memo[args]
      return memo[args]
    else:
      rv = function(*args)
      memo[args] = rv
      return rv
  return wrapper




class IndexDict(dict):
  ref = {0:'x',1:'y',2:'z'}
  full = {3:'cmd',4:'index',5:'i',6:'j'}
  full.update(ref)
  def __init__(self, *args, **kwargs):
    # self._setname(name)
    # self.name = name
    dict.__init__(self, *args, **kwargs)
    if 'name' in self: self._setname(self['name'])
  def _setname(self,name=None):
    ''' Set the name to be something'''
    if name is not None:
      self.name = name
    else:
       self.name = "G%02d"%self.cmd

  def updateName(self):
    ''' update the name to be the command'''
    self._setname()

  def __getitem__(self,key):
    '''automatically return x,y,z for 0,1,2'''
    if isinstance(key,int) and key in self.full and self.full[key] in self.allkeys():
      return dict.get(self,self.full[key])
    if isinstance(key,slice):
      return [self[ii] for ii in xrange(*key.indices(len(self)))]
    elif isinstance(key, str) and key.lower() in self.allkeys():
      return dict.get(self,key.lower())
    else:
      return float('nan')

  def __setitem__(self,key,value):
    ''' automatically set all values of ref'''
    if isinstance(key,int) and key in self.full:
      dict.__setitem__(self,self.full[key].lower(),value)
      if key == 3: self._setname()
    else:
      dict.__setitem__(self,key.lower(),value)

  def __getattr__(self,name):
    ''' relate .x to ['x'] '''
    if name in self.allkeys():
      return self[name]
    else:
      return dict.get(self,name)

  def __setattr__(self, name, value):
    if name in self.allkeys():
      self[name] = value
    else:
      dict.__setitem__(self,name,value)


  def __repr__(self):
    if self.cmd == 2:
      return '%s:(x=% .3f, y=% .3f, i=% .3f, j=% .3f)'%(self.name, self[0],self[1],self[5],self[6])
    else:
      return '%s:(% .3f,% .3f,% .3f)'%(self.name, self[0],self[1],self[2])
  
  def toGcode(self):
    ''' attempts to convert '''
    if self.cmd == 2:
      return 'G%02i   X%.3f Y%.3f I%.3f J%.3f'%(self.cmd,self.x,self.y, self.i, self.j)
    else:
      return 'G%02i   X%.3f Y%.3f Z%.3f'%(self.cmd,self.x,self.y,self.z)


  # for x in tool:
  # this should give the x,y,z axis labels like a dictionary
  def __iter__(self):
    self._current = 0
    return self
  def next(self):
    if self._current > len(self.ref.keys())-1:
      raise StopIteration
    else:
      self._current += 1
      return self.ref[self._current - 1]

  # sometimes we want everything
  def allkeys(self):
    return dict.keys(self)
  def allvalues(self):
    return dict.values(self)

  def keys(self):
    return sorted([self.ref[k] for k in self.ref])
  def values(self):
    return [self.get(k) for k in self.keys()]

  def upReturn(self,key,value):
    ''' update key with value and then return'''
    self[key] = value
    return self
    return deepcopy(self)

  # # give this item a hash property so that we can do ItemDict[0:2]
  # WHAT DOES HASH DO?
  # def __hash__(self):
  #   return hash(self.keys())

  # start at (0,0,0) rater than nans
  @classmethod
  def setorigin(s):
    self = IndexDict(name=' origin')
    self.cmd = 0
    self.index = -1
    for key in self.ref:
      self[self.ref[key]] = 0.0
    return self


if __name__ == '__main__':
  print 'testing ItemDict:'
  d = IndexDict.setorigin()
  print d[0], d.x, d['x'] # should be ok for x,y,z
  print d['cmd'], d.cmd, d['index'],d.index # should be ok for index
  d.y = 1
  print d[1], d.y, d['y']

  for item in d:
    print item # returns the labels like a dictionary

  print d[0:3]# x,y,z
  print d[0:4] # x,y,z,cmd
  print d[0:10] # well that is probably not good
  print d.keys()
  print d.values()

  print ' reset'
  e = IndexDict(d)
  print d
  print e




