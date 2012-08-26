#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez 
import os, re, sys
from datetime import datetime
from random import uniform
from lib.clint.textui import puts, colored
from lib.util import deltaTime

from numpy import arange, floor, ceil
from pyx import *


RED   = (1.0,0.0,0.0)
BLUE  = (0.0,0.0,1.0)
GREEN = (0.15,0.7,0.15)
BLACK = [0.0,0.0,0.0]
LIGHTBLUE =  (0.5,0.5,1.0)
LIGHTRED = (1.0,0.5,0.5)

class Image(object):
  def __init__(self, filename=None, 
               gridscale=1.0,
               gridsize=[[0.0,1.0],[0.0,1.0]],
               pagesize=(5,4),  # width,height [in]
               pagemargin=(0.5,0.5,0.5,0.5)):
    ''' Image Canvas with milling functions. 
    gridscale : [Float] multiplication factor for grid size
    gridsize  : [Inches] The physical space to span. [[xmin,xmax],[ymin,ymax]]
    pagesize  : [inches] Can be (width,height) or 'letter','letter*', 'A3',A4'
                 Append * to get landscape.
    pagemargin : [inches] Top, right, bottom, left margins.'''
    self.filename = os.path.expanduser(os.path.expandvars(filename))
    gridsize = [[floor(x[0]*1.05), ceil(x[1]*1.05)] for x in gridsize]
    self.gridsize = gridsize
    self.pagesize = pagesize
    unit.set(defaultunit="inch")
    self.g = graph.graphxy(width=pagesize[0], 
                           height=pagesize[1],
                      x=graph.axis.linear(min=gridsize[0][0], 
                                          max=gridsize[0][1],
                                          title='X [inch]'),
                      y=graph.axis.linear(min=gridsize[1][0], 
                                          max=gridsize[1][1],
                                          title='Y [inch]'))

  def __enter__(self):
    '''with constructor :: generate a nice plot with a plot and axis'''
    return self
    
  def __exit__(self, type, value, traceback):
    '''with constructor finished -- close anything open.'''
    start = datetime.now()
    print 'Writing : %s'%self.filename
    self.g.writeEPSfile(self.filename)
    print '  ! Finished %s'%deltaTime(start)
    return isinstance(value, TypeError)
  

   # the invidual plot commands

  def mill(self,xarr,yarr, 
            color=color.rgb.blue, 
            width=0.010): # in inches
    '''Mill an x,y array defaults to red and 10mil paths.'''
    self.g.plot(graph.data.points(zip(xarr, yarr), x=1, y=2),
            [graph.style.line([style.linewidth(width*unit.w_inch), 
                               color, style.linestyle.solid])])

  def move(self,xarr,yarr, 
            color=color.cmyk.Gray,
            width=style.linewidth.thin):
    '''Moves the bit around (x,y) defaults to light blue and 1 point ('onepoint'),
    can pass a inch float as well.  '''
    self.g.plot(graph.data.points(zip(xarr, yarr), x=1, y=2),
            [graph.style.line([width, color, style.linestyle.solid])])

  def drill(self,x,y,
            r=0.032, 
            color=None, 
            outlinewidth=0.001,
            outlinecolor=color.rgb.blue):
    ''' A nice drill hole cross and defaults to 32mil holes'''
    self.g.plot(graph.data.points(zip(x,y),x=1,y=2),
                  [graph.style.symbol(graph.style.symbol.circle, size=r*unit.w_inch,
                                      symbolattrs=[deco.stroked([outlinecolor])])])


