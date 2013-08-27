#!/usr/bin/env python
# util.py : some nice things
# [2012.07.30] - Mendez

# [System]
import sys
from datetime import datetime
from math import sqrt

# [Installed]
from clint.textui import colored, puts, indent


def error(message):
  '''Nice little error message for the user that shuts down options'''
  puts(colored.red('\n !!! '+message))
  sys.exit(1)



def deltaTime(start=None):
  '''From a start datetime object get a nice string of 'x hours, y minutes, z seconds'
  of time passed since the start. '''
  if start is None:
    return datetime.now()
  
  diff = datetime.now() - start
  # Calculate the number of sections in the 
  seconds = diff.days*86400 + diff.seconds + diff.microseconds/float(10**6)
  out = []
  epocs = [ [3600,'hour'],
            [60,'minute'],
            [1,'second'],
            [0.001,'milisecond'] ]
  factors,_ = zip(*epocs)
  
  # For each epoc item break decimate the total number of seconds
  while seconds > min(factors):
    for factor, noun in epocs:
      if seconds >= factor:
        delta = int(seconds / factor)
        if delta > 1:
            noun +='s'
        out.append('%d %s'%(delta,noun))
        seconds -= factor * delta
  
  # join them up a nice string
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

def cprint(*args, **kwargs):
  '''Colorful print.  
  set color=['blue','green','red', ...] to set the color.
  defaults to no color if not specified.
  if bad color then is blue'''
  color = kwargs.get('color', None)
  
  if color is None:
    fcn = lambda x : x
  else:
    fcn = getattr(colored, color, colored.blue)
  puts(fcn(*args))
    


