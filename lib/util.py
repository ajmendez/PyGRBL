#!/usr/bin/env python
# util.py : some nice things
# [2012.07.30] - Mendez
import sys
from datetime import datetime
from math import sqrt
from clint.textui import colored, puts, indent


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
  '''euclidean distance of two lists. TODO should be generalized...'''
  return sqrt(sum([pow(alpha-beta,2) for alpha,beta in zip(A,B)]))


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
  full = {3:'cmd',4:'index'}
  full.update(ref)
  def __init__(self,name='IndexDict', *args, **kwargs):
    self.name = name
    dict.__init__(self, *args, **kwargs)

  def __getitem__(self,key):
    '''automatically return x,y,z for 0,1,2'''
    if isinstance(key,int) and key in self.full and self.full[key] in self.allkeys():
      return dict.get(self,self.full[key])
    elif isinstance(key, str) and key.lower() in self.allkeys():
      return dict.get(self,key.lower())
    else:
      return float('nan')

  def __setitem__(self,key,value):
    ''' automatically set all values of ref'''
    if isinstance(key,int) and key in self.full:
      dict.__setitem__(self,self.full[key].lower(),value)
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
    return '%s:(% .3f, % .3f, % .3f)'%(self.name, self[0],self[1],self[2])
  
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

  # give this item a hash property so that we can do ItemDict[0:2]
  def keys(self):
    return sorted([self.ref[k] for k in self.ref])
  def __hash__(self):
    return hash(self.keys())

  # start at (0,0,0) rater than nans
  @classmethod
  def setorigin(s):
    self = IndexDict(name=' origin')
    self.cmd = 0
    for key in self.ref:
      self[self.ref[key]] = 0.0
    return self