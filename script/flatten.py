#!/usr/bin/env python
# flatten.py : Prints out a simple gcode flatten script
# [2012.01.31] Mendez

# What we are going with.
xmax = 3.75         # inch : max x dimension of milled out area
ymax = 5.35         # inch : max y dimension of milled out area
bitsize = (1/8.)/2. # inch : Radius of mill bit.
milldepth = -0.130  # inch : milling depth

HEADER = '''\
G20 (inch)
G90 (absolute)
G00 X0.000 Y0.000 Z0.000
'''

print HEADER
print '(Flatten the board)'
print 'G01 Z%.3f'%(milldepth)
for x in range(0,int(xmax/bitsize)):
  if not x%2:
    if x > 1: print 'G01 X%f Y%f'%((x-2)*bitsize,0)
    print 'G01 X%f Y%f'%(x*bitsize,0)
    print 'G01 X%f Y%f'%(x*bitsize,ymax)
  else:
    if x > 2: print 'G01 X%f Y%f'%((x-2)*bitsize,ymax)
    print 'G01 X%f Y%f'%(x*bitsize,ymax)
    print 'G01 X%f Y%f'%(x*bitsize,0)

def routecorner(x,y):
  '''Route a pocket in each corner so that the round bit will not interfer with
  the square corner of the board. '''
  print 'G01 X%f Y%f'%(x,y)
  print 'G01 X%f Y%f'%(x-bitsize,y)
  print 'G01 X%f Y%f'%(x-bitsize,y-bitsize)
  print 'G01 X%f Y%f'%(x+bitsize,y-bitsize)
  print 'G01 X%f Y%f'%(x+bitsize,y+bitsize)
  print 'G01 X%f Y%f'%(x-bitsize,y+bitsize)
  print 'G01 X%f Y%f'%(x-bitsize,y)
  print 'G01 X%f Y%f'%(x,y)

print '(route some corners)'
routecorner(0.,0.)
routecorner(0.,ymax)
routecorner(xmax,ymax)
routecorner(xmax,0)
routecorner(0,0)

# raise and go back to zero zero
print '''\
G00 Z0.000
G00 X0.0 Y0.0
'''
    
