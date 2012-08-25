#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez 
import os, re, sys
from random import uniform
from canvas import FancyCanvas
# '''http://www.seehuhn.de/pages/psfile#sec:2.0.0'''

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
               pagesize='letter', 
               pagemargin=(0.5,0.5,0.5,0.5)):
    ''' Image Canvas with milling functions. 
    gridscale : [Float] multiplication factor for grid size
    gridsize  : [Inches] The physical space to span. [[xmin,xmax],[ymin,ymax]]
    pagesize  : [inches] Can be (width,height) or 'letter','letter*', 'A3',A4'
                 Append * to get landscape.
    pagemargin : [inches] Top, right, bottom, left margins.'''
    self.filename = os.path.expanduser(os.path.expandvars(filename))
    self.gridscale = gridscale
    self.gridsize = gridsize
    self.pagesize = pagesize
    self.pagemargin = pagemargin
    self.c = FancyCanvas(self.filename,
      margin_top=pagemargin[0],
      margin_right=pagemargin[1],
      margin_bottom=pagemargin[2],
      margin_left=pagemargin[3],
      paper=pagesize,
      title='image.py : pyGRBL visualiztion',
      creator='[PyGRBL :: Mendez]')
    
  def __enter__(self):
    '''with constructor :: generate a nice plot with a plot and axis'''
    self.setupGrid()
    self.setupPlot()
    return self
    
  def __exit__(self, type, value, traceback):
    '''with constructor finished -- close anything open.'''
    self.c.close()
    return isinstance(value, TypeError)
  


  def mill(self,xarr,yarr, 
            color=BLUE, 
            width=0.010):
    '''Mill an x,y array defaults to red and 10mil paths.'''
    self.c.array(xarr,yarr, color=color, width=width)

  def move(self,xarr,yarr, 
            color=LIGHTBLUE,
            width='onepoint'):
    '''Moves the bit around (x,y) defaults to light blue and 1 point ('onepoint'),
    can pass a inch float as well.  '''
    self.c.array(xarr,yarr, color=color, width=width)

  def drill(self,x,y,
            r=0.032, 
            color=None, 
            outlinewidth=0.001,
            outlinecolor=BLACK):
    ''' A nice drill hole cross and defaults to 32mil holes'''
    self.c.circle(x,y,r, color=color, 
                    outlinecolor=outlinecolor, 
                    withcross=True,
                    outlinewidth=outlinewidth)



  def setupGrid(self, graphmarginpercent=0.05):
    ''' Ensure that the Gridscale and gridsize are correctly setup
    Here is the basic idea:
     +--Page+Margins-------------------------+
     |                                       |
     |   +---DrawingArea------------------+  |
     |   |                                |  |
     |   |                                |  |
     |   |    +----GRID---------------+   |  |
     |   |    |       ^               |   |  |
     |   |    |       |               |   |  |
     |   |    |      y[1]             |   |  |
     |   |    |       |               |   |  |
     |   |    |<-x[0]-+-AXIS---x[1]-->|   |  |
     |   |    |       |               |   |  |
     |   |    |       |               |   |  |
     |   |    |      y[[0]            |   |  |
     |   |    |       |               |   |  |
     |   |    |       v               |   |  |
     |   |    +-----------------------+   |  |
     |   |    ^                           |  |
     |   |    |                           |  |
     |   |    |                           |  |
     |   |    |                           |  |
     |   |   o[1]                         |  |
     |   |    |                           |  |
     |   |    |                           |  |
     |   |o[0]+                           |  |
     |   |+--->                           |  |
     |   +--------------------------------+  |
     |  (0,0)                                |
     +---------------------------------------+
     '''
    size = self.c.size()
    grange = []
    gedge = [] # the left bottom edge
    gscale = [] # how much to scale up to page size
    
    print self.gridsize

    # Loop over axis to find new gscale and ranges
    for i,(d,s) in enumerate(zip(self.gridsize,size)):
      grange.append( abs(d[1]-d[0])*(1.0+2*graphmarginpercent) ) # the total x/y range
      gedge.append( (d[0])*(1.0+graphmarginpercent) ) # left border
      gscale.append( s/grange[i] ) # maximum scale that this axis would go
    gscale = min(gscale) # take the smallest scale factor so height and width match

    zero = [] # left bottom edge of the plot
    gzero = [] # the grid origin
    for i,(dim,gdim,ge) in enumerate(zip(size,grange,gedge)):
      zero.append( (dim - gscale*gdim)/2.0 )
      gzero.append( zero[i]+gscale*abs(ge) )

    self.gscale = gscale
    self.grange = grange # grid range
    self.gedge = gedge   # grid left bottom edge
    self.gzero = gzero    # grid origin
    self.edge = zero     # paper space of the left bottom edge

    self.c.setcolor(LIGHTBLUE)
    self.c.circle(zero[0],zero[1],r=0.1)
    self.c.line(zero[0],zero[1],zero[0], zero[1]+gscale*grange[1])
    self.c.line(zero[0],zero[1],zero[0]+gscale*grange[0], zero[1])
    self.c._stroke()

    self.c.setcolor(LIGHTRED)
    self.c.circle(gzero[0],gzero[1],r=0.1)
    self.c.line(gzero[0],gzero[1],gzero[0], gzero[1]-gscale*abs(gedge[1]))
    self.c.line(gzero[0],gzero[1],gzero[0]-gscale*abs(gedge[0]), gzero[1])
    self.c.line(gzero[0],gzero[1],gzero[0], gzero[1]+gscale*(grange[1]-abs(gedge[1])))
    self.c.line(gzero[0],gzero[1],gzero[0]+gscale*(grange[0]-abs(gedge[0])), gzero[1])
    self.c._stroke()


  def setupPlot(self):
    self.c.grid(self.edge, self.gedge, self.grange, self.gscale)

    # x = [0.5,1.5,2.0,3.0]
    # y = [0.5,0.5,1.0,3.0]
    # self.move(x,y)
    # for a,b in zip(x,y): self.drill(a,b)

    # x =[1,2.25,2.5]
    # y = [2,1.25,2.5]
    # self.mill(x,y)
