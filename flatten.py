#!/usr/bin/env python
# flatten.py
# Output a simple gcode flatten script
# [2012.01.31] Mendez

# Full motion
# xmax=4.33 # inches
# ymax=2.36 # sinches


# What we are going with.
xmax=3.75 # inches -- 95
ymax=5.3 # inches  -- 140mm
# xmax=0.75 # inches -- 95
# ymax=5.2 # inches  -- 140mm

bitsize = 1/8./2.

print '''G20
G90
G00 X0.00 Y0.00 Z0

'''
# G01 X0.00 Y0.00 Z-0.130

# for x in range(0,int(xmax/bitsize)):
#   # for y in range(0,int(ymax/bitsize)):
#     
#   # print 'G01 Y0'
#   # print 'G01 X%f'%(x*bitsize)
#   # print 'G01 Y%f'%(ymax)
#   
#   if not x%2:
#     if x > 1:
#       print 'G01 X%f Y%f'%((x-2)*bitsize,0)
#     print 'G01 X%f Y%f'%(x*bitsize,0)
#     print 'G01 X%f Y%f'%(x*bitsize,ymax)
#   else:
#     if x > 2:
#       print 'G01 X%f Y%f'%((x-2)*bitsize,ymax)
#     print 'G01 X%f Y%f'%(x*bitsize,ymax)
#     print 'G01 X%f Y%f'%(x*bitsize,0)

def routecorner(x,y):
  print 'G01 X%f Y%f'%(x,y)
  print 'G01 X%f Y%f'%(x-bitsize,y)
  print 'G01 X%f Y%f'%(x-bitsize,y-bitsize)
  print 'G01 X%f Y%f'%(x+bitsize,y-bitsize)
  print 'G01 X%f Y%f'%(x+bitsize,y+bitsize)
  print 'G01 X%f Y%f'%(x-bitsize,y+bitsize)
  print 'G01 X%f Y%f'%(x-bitsize,y)
  print 'G01 X%f Y%f'%(x,y)

routecorner(0.,0.)
routecorner(0.,ymax)
routecorner(xmax,ymax)
routecorner(xmax,0)
routecorner(0,0)
  # if x%2: 
  #   yran = range(0,int(ymax/bitsize))
  # else:
  #   yran = range(int(ymax/bitsize),0,-1)
  # for y in yran:
  #   print 'G01 X%f Y%f'%(x*bitsize,y*bitsize)

print '''G00 Z0.000
G00 X0.0 Y0.0
'''
    
