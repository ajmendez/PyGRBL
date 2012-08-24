#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez 
import os, re
from psfile import PSFile
from random import uniform

# '''http://www.seehuhn.de/pages/psfile#sec:2.0.0'''

TITLE='Visualize.py : pyGRBL visualiztion'
INS = lambda x: 72.00 * x    # inches-to-points
FNS = lambda x: x/72.00      # points to inches
PNS = lambda x: int(FNS(x))  # points-to-inches -- int

RED   = (1.0,0.0,0.0)
BLUE  = (0.0,0.0,1.0)
GREEN = (0.15,0.7,0.15)
BLACK = [0.0,0.0,0.0]

class FancyCanvas(PSFile):
  def __init__(self, *args, **kwargs):
    '''Get me some extra nice variables'''
    self.location=[0.0,0.0]
    self.fontsize=10
    super(FancyCanvas,self).__init__(*args, **kwargs)
    self.append('/Helvetica %s selectfont'%self.fontsize)
    self.define('l','lineto')
    self.define('rl','rlineto')
    self.define('m','moveto')
    self.define('rm','rmoveto')

  def _move(self,x,y):
    self.append("%.1f %.1f m"%(INS(x), INS(y)))
  def _rmove(self,dx,dy):
    self.append("%.1f %.1f rm"%(INS(dx), INS(dy)))
  def _rotate(self,r):
    self.append('%.2f rotate'%r)
  def _line(self,x,y):
    self.append("%.1f %.1f l"%(INS(x),INS(y)))
  def _rline(self,x,y):
    self.append("%.1f %.1f rl"%(INS(x),INS(y)))
  def _arc(self,x,y,r,a=0,b=360):
    self.append("%.1f %.1f %0.1f %0.1f %0.1f arc"%(INS(x),INS(y), INS(r), a, b))
  def _rgbcolor(self,color):
    self.append('%.2f %.2f %.2f setrgbcolor'%(color))
  def _graycolor(self,c):
    self.append('%.2f setgray'%(c))
  def _stroke(self):
    self.append('stroke')
  def _fill(self):
    self.append('fill')
  def _save(self):
    self.append('gsave')
  def _restore(self):
    self.append('grestore')
  def _text(self,t):
    self.append("(%s) show"%t)
  def _width(self,w):
    self.append("%.1f setlinewidth"%(INS(w)))


  def setcolor(self,color=None):
    ''' Color setup '''
    if color is not None: 
      if (isinstance(color,tuple) or isinstance(color,list)) and len(color) == 3:
        self._rgbcolor(tuple(color))
        return True
      elif isinstance(color,float) or isinstance(color,int):
        self._graycolor(color)
        return True
      else:
        print 'Failed to colorify: %s'%(str(color))
    return False
  def uncolor(self):
    '''return color back to black'''
    self.color(0)

  def setwidth(self,width=None):
    if width is not None and width > 0:
      self._width(width)



  def text(self,x,y,text,
      rotate=None,
      reverse=False,
      color=None):
    '''prints out a message to x,y'''
    if rotate:
      offset = [self.fontsize/(-2.0),self.fontsize*2]
      if reverse: offset[1] *= -0.25
    else:
      offset = [self.fontsize*2,self.fontsize/2.0]
      if reverse: offset[0] *= -0.25
    offset =[FNS(o) for o in offset]
    # offset =[PNS(o) for o in offset]
    self._move(x-offset[0], y-offset[1])
    # self.append("%.3f %.3f moveto"%(INS(x)-offset[0],INS(y)-offset[1]))
    if rotate: self._rotate(rotate)
    colored = self.setcolor(color)
    self._text(text)
    if rotate: self._rotate(-rotate)
    if colored: self._stroke()

  def point(self,x,y, color=None):
    self.setcolor(color)
    self._arc(x,y,1)
    self._fill(x,y,1)

  def circle(self,x,y,r, 
              color=None, 
              outlinewidth=None,
              withcross=False,
              _outsidecross=1.25,
              outlinecolor=None):
    # print x,y,r,color,outlinecolor
    self._arc(x,y,r)
    if withcross:
      d = r*_outsidecross
      self.line(x-d,y,x+d,y)
      self.line(x,y-d,x,y+d)
    self._save() # save outline to then stroke
    colored = self.setcolor(color)
    if colored: 
      self._fill()
      self._restore()
    self.setwidth(outlinewidth)
    if outlinecolor: self.setcolor(outlinecolor)
    self._stroke()




  def line(self,x,y,x2,y2, color=None, width=None):
    '''Draw a line'''
    colored = self.setcolor(color)
    self.setwidth(width)
    self._move(x,y)
    self._line(x2,y2)
    if colored: self._stroke()

  def tickline(self,x,y,x2,y2,
               notext=False,
               reverse=False,
               color=None, 
               ndivisions=4, 
               ticklen=0.2):
    '''Tick the axis
          ndivisions : number of times to subdivide up the range
          ticklen : the fraction of the range that becomes the length of the ticks'''
    colored = self.setcolor(color)

    isx = (y == y2) # if no height difference we are doing the x axis
    value = (x,x2) if isx else (y,y2)
    rotate = 90 if isx else 0
    delta = abs(value[1]-value[0])
    if reverse: delta *= -1.0

    # draw the line
    self.line(x,y,x2,y2)

    ntick = 2**(ndivisions)
    for i in range(ntick):
      length = delta*ticklen
      # if we are at a binary division of the length scale down the ticklen
      for j in range(ndivisions): 
        if (i % (2**j) > 0) : length /= 2

      if isx:
        x0 = (i/float(ntick))*abs(x2-x) + x
        self.line(x0,y,x0,y2+length)
      else:
        y0 = (i/float(ntick))*abs(y2-y) + y
        self.line(x,y0,x2+length,y0)
    if not notext: self.text(x2,y2,"%.1f"%(value[1]), 
                             rotate=rotate, reverse=reverse)
    if colored: self._stroke()



  def grid(self, axiscolor=0.1, gridcolor=0.9):
    '''Makes a nice graph on the postscript'''
    height = PNS(self.height)# - 2*self.margin[0])
    width = PNS(self.width)# - 2*self.margin[1])
    
    # plot a grid
    for x in range(width):
      for y in range(height):
        if x == 0: self.tickline(x,y,x,y+1,color=axiscolor)
        if x == width-1: self.tickline(x+1,y,x+1,y+1,color=axiscolor, reverse=True, notext=True)
        if y == 0: self.tickline(x,y,x+1,y,color=axiscolor)
        if y == height-1: self.tickline(x,y+1,x+1,y+1,color=axiscolor, reverse=True, notext=True)
        colored = self.setcolor(gridcolor)
        if x != width-1: self.line(x+1,y,x+1,y+1)
        if y != height-1: self.line(x,y+1,x+1,y+1)
        if colored: self._stroke()
    self._stroke()

  

  def array(self, xarr, yarr, 
            color=None,
            width=None):
    '''Strokes an array'''
    colored = self.setcolor(color)
    self.setwidth(width)
    for i, (x,y) in enumerate(zip(xarr,yarr)):
      if i == 0 : 
        self._move(x,y)
        x0, y0 = x, y
      else:
        self._rline(x-x0,y-y0)
        x0, y0 = x, y
    self._stroke() # finish no matter what.







class Image(object):
  def __init__(self, filename=None, size=None, margin=None):
    if not size: size = [8.0,8.0] # width, height in inches
    if not margin: margin=[0.5,0.5,0.5,0.5] # top,right,bottom,left inches

    if filename: filename = os.path.expanduser(os.path.expandvars(filename))
    self.margin = margin
    self.size = size
    self.width = size[0]
    self.height = size[1]
    self.filename = filename
    self.c = FancyCanvas(filename,
      margin_top=INS(margin[0]),
      margin_right=INS(margin[1]),
      margin_bottom=INS(margin[2]),
      margin_left=INS(margin[3]),
      paper=(INS(self.width),INS(self.height)),
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
