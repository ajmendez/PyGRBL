#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez 
import os, re, sys
from datetime import datetime
from random import uniform
from lib.clint.textui import puts, colored
from lib.util import deltaTime

import matplotlib
matplotlib.use('ps')
from matplotlib import pyplot as plt
from matplotlib import rc
# from pylab import setp, gca
from numpy import arange, floor, ceil


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
    gridsize = [[floor(x[0]), ceil(x[1])] for x in gridsize]
    # gridsize = [j for i in gridsize for j in i]
    self.gridsize = gridsize
    self.pagesize = pagesize

    fig = plt.figure(figsize=self.pagesize, linewidth=2)
    fig.subplots_adjust(left=None,
                        bottom=0.2,
                        right=None,
                        top=0.97,
                        wspace=None,
                        hspace=None)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.autoscale(False)

    ax.set_xlabel('X [inch]')
    ax.set_xlim(gridsize[0])
    plt.setp(ax.get_xticklabels(), rotation='vertical')

    ax.grid(True, 'major', color='w', linestyle='-', linewidth=1.4)
    ax.grid(True, 'minor', color='0.92', linestyle='-', linewidth=0.7)
    ax.patch.set_facecolor('0.85')
    ax.set_axisbelow(True)
    

    from matplotlib.ticker import MaxNLocator
    class mendezLocator(MaxNLocator):
      def pabl(self):
        pass
    # ax.tick_params(which='both', width=2)
    # ax.tick_params(which='major', length=7)
    # ax.tick_params(which='minor', length=4, color='r')

    ax.set_ylabel('Y [inch]')
    ax.set_ylim(gridsize[1])

    x = arange(-10.,10.,1)
    y = x
    ax.plot(x,y)
    plt.savefig('fig1.ps', dpi=150,format='ps')

    
    


  def __enter__(self):
    '''with constructor :: generate a nice plot with a plot and axis'''
    
    return self
    
  def __exit__(self, type, value, traceback):
    '''with constructor finished -- close anything open.'''
    return isinstance(value, TypeError)
  

   # the invidual plot commands

  def mill(self,xarr,yarr, 
            color=BLUE, 
            width=0.010):
    '''Mill an x,y array defaults to red and 10mil paths.'''
    # self.c.array(xarr,yarr, color=color, width=width)
    pass

  def move(self,xarr,yarr, 
            color=LIGHTBLUE,
            width='onepoint'):
    '''Moves the bit around (x,y) defaults to light blue and 1 point ('onepoint'),
    can pass a inch float as well.  '''
    # self.c.array(xarr,yarr, color=color, width=width)
    pass

  def drill(self,x,y,
            r=0.032, 
            color=None, 
            outlinewidth=0.001,
            outlinecolor=BLACK):
    ''' A nice drill hole cross and defaults to 32mil holes'''
    # self.c.circle(x,y,r, color=color, 
    #                 outlinecolor=outlinecolor, 
    #                 withcross=True,
    #                 outlinewidth=outlinewidth)
    pass

