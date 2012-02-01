#!/usr/bin/env python
# flatten script

# xmax=4.33 # inches
# ymax=2.36 # sinches
xmax=3.74 # inches -- 95
ymax=5.4 # inches  -- 140mm

bitsize=0.03

print '''G20
G90
G00 X0.00 Y0.00 Z0.00
'''

for x in range(0,int(xmax/bitsize)):
  # for y in range(0,int(ymax/bitsize)):
    
  # print 'G01 Y0'
  # print 'G01 X%f'%(x*bitsize)
  # print 'G01 Y%f'%(ymax)
  
  # if not x%2: 
  #   print 'G01 X%f Y%f'%(x*bitsize,0)
  #   print 'G01 X%f Y%f'%(x*bitsize,ymax)
  # else:
  #   print 'G01 X%f Y%f'%(x*bitsize,ymax)
  #   print 'G01 X%f Y%f'%(x*bitsize,0)
  
  if x%2: 
    yran = range(0,int(ymax/bitsize))
  else:
    yran = range(int(ymax/bitsize),0,-1)
  for y in yran:
    print 'G01 X%f Y%f'%(x*bitsize,y*bitsize)

print '''G00 Z0.500
G00 X0.0 Y0.0
'''
    