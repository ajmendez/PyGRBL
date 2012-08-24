#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez 
import os, re
from random import uniform
from canvas import FancyCanvas
# '''http://www.seehuhn.de/pages/psfile#sec:2.0.0'''

TITLE='Visualize.py : pyGRBL visualiztion'

RED   = (1.0,0.0,0.0)
BLUE  = (0.0,0.0,1.0)
GREEN = (0.15,0.7,0.15)
BLACK = [0.0,0.0,0.0]


class Image(object):
  def __init__(self, filename=None, size=None, margin=None):
    if not size: size = [8.0,8.0] # width, height in inches
    print size
    if not margin: margin=[0.5,0.5,0.5,0.5] # top,right,bottom,left inches

    if filename: filename = os.path.expanduser(os.path.expandvars(filename))
    self.margin = margin
    self.size = size
    self.width = size[0]
    self.height = size[1]
    self.filename = filename
    self.c = FancyCanvas(filename,
      margin_top=margin[0],
      margin_right=margin[1],
      margin_bottom=margin[2],
      margin_left=margin[3],
      paper=(self.width,self.height),
      # margin_top=INS(margin[0]),
      # margin_right=INS(margin[1]),
      # margin_bottom=INS(margin[2]),
      # margin_left=INS(margin[3]),
      # paper=(INS(self.width),INS(self.height)),
      title=TITLE,
      creator='[PyGRBL :: Mendez]')
    
  def __enter__(self):
    '''with constructor :: builds a nice'''
    self.setupPlot()
    return self
    
  def __exit__(self, type, value, traceback):
    '''with constructor finished.'''
    self.c.close()
    return isinstance(value, TypeError)
  
  def mill(self,xarr,yarr, 
            color=RED, 
            width=0.010):
    self.c.array(xarr,yarr, color=color, width=width)

  def move(self,xarr,yarr, 
            color=BLUE,
            width=0.001):
    self.c.array(xarr,yarr, color=color, width=width)

  def drill(self,x,y,
            r=0.032, 
            color=None, 
            outlinewidth=0.001,
            outlinecolor=BLACK):
    self.c.circle(x,y,r, color=color, 
                    outlinecolor=outlinecolor, 
                    withcross=True,
                    outlinewidth=outlinewidth)


  def setupPlot(self):
    self.c.grid()
    # x = [0.5,1.5,2.0,3.0]
    # y = [0.5,0.5,1.0,3.0]
    # self.move(x,y)
    # for a,b in zip(x,y): self.drill(a,b)

    # x =[1,2.25,2.5]
    # y = [2,1.25,2.5]
    # self.mill(x,y)
