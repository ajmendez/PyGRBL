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