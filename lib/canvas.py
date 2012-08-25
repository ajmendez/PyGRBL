#!/usr/bin/env python
# canvas.py : a nice little plot surface to plot to ps with.
# [2012.08.24] - Mendez 
from psfile import PSFile
import collections
from numpy import arange, floor, ceil

INS = lambda x: 72.00 * x    # inches-to-points
FNS = lambda x: x/72.00      # points to inches
PNS = lambda x: int(FNS(x))  # points-to-inches -- int

class OLDCanvas(PSFile):
  def __init__(self, *args, **kwargs):
    '''Get me some extra nice variables by default convert inches to points'''
    self.fontsize=10

    # do some nice unit conversion so that I dont have to
    items = ['paper', 'margin_top','margin_right','margin_bottom','margin_left']
    for item in items:
      if item in kwargs:
        x = kwargs[item]
        # print item, x, isinstance(x,collections.Iterable)
        if isinstance(x,str):
          # for "letter" and the sort
          pass
        elif isinstance(x, collections.Iterable):
            x = tuple(map(INS, x)) #HACK
        else:
          x = INS(x)
        kwargs[item] = x

    super(FancyCanvas,self).__init__(*args, **kwargs)
    self.append('/Helvetica %s selectfont'%self.fontsize)
    self.define('l','lineto')
    self.define('rl','rlineto')
    self.define('m','moveto')
    self.define('rm','rmoveto')

  def size(self):
    '''Return the inches version of the size'''
    return (FNS(self.width),FNS(self.height))


  # internal PSFile appends. all are here so that we can abstract away from them
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
    ''' Sets the current color for any stroke / fill operation.  One needs to be sure
    that they _stroke() once they finish that set of lines with a color.
    returns True if we have applied a color.
    should handle:
    (red, blue, green) float tuple of rgb colors
    (grey) float of grey value [FIXME]
    None no color change'''
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

  def setwidth(self,width=None):
    ''' set the line width for any stroke command.  After you have a line and you
    want to change line widths, you need to _stroke().  
    width in [inches].
    Returns True if changed width'''
    widthdict = dict(onepoint=1/72.0)
    if width is not None and width > 0:
      if isinstance(width,str):
        self._width(widthdict[width])
      else:
        self._width(width)
      return True
    return False



  def text(self,x,y,text,
           rotate=None, # Angle in degrees to rotate the text.
           reverse=False, # HACK -- reverses the offset [FIXME]
           color=None):   # color to apply 
    '''Writes a string of text to the screen at (x,y).  
    Need to fix the x,y location and add some nice formatitng bits.
    Should be close to x,y with some nice offset.'''
    if rotate:
      offset = [self.fontsize/(-2.0),self.fontsize*2]
      if reverse: offset[1] *= -0.25
    else:
      offset = [self.fontsize*2,self.fontsize/2.0]
      if reverse: offset[0] *= -0.25
    offset =[FNS(o) for o in offset] # fns converts the offset[points] into inches for x,y

    # move to location, rotate if needed, color, write text, unrotate, uncolor
    self._move(x-offset[0], y-offset[1])
    if rotate: self._rotate(rotate)
    colored = self.setcolor(color)
    self._text(text)
    if rotate: self._rotate(-rotate)
    if colored: self._stroke()

  def point(self,x,y, color=None):
    '''Draws a nice point at x,y with some color'''
    colored = self.setcolor(color)
    self._arc(x,y,1)
    self._fill(x,y,1)
    if colored: self._stroke()

  def circle(self,x,y,r, 
              color=None, 
              outlinewidth=None, # width in inches of the line.
              withcross=False,
              _outsidecross=1.25,
              outlinecolor=None):
    '''plots a circle at (x,y) with radius r.
    color         -- [COLOR] fill color : None == no fill
    outlinewidth  -- [F_INCHES]stroke width in inches
    outlinecolor  -- [COLOR] outline color : None == no color
    _outsidecross -- [T/F] adds a nice line that crosses at the center (x,y) that extends beyond circle
    '''
    self._arc(x,y,r)
    if withcross:
      d = r*_outsidecross
      self.line(x-d,y,x+d,y)
      self.line(x,y-d,x,y+d)
    # fill clears the current path, so we save it, so that we can stroke it afterwards
    self._save()
    colored = self.setcolor(color)
    if colored: 
      self._fill()
      self._restore()
    self.setwidth(outlinewidth)
    if outlinecolor: self.setcolor(outlinecolor)
    self._stroke()




  def line(self,x,y,x2,y2, color=None, width=None):
    '''Draw a line from (x,y) to (x2,y2). This should be used for one off lines.  
    Use array() for a long path to be plotted.
    color -- [COLOR] color of the line
    width -- [INCHES] width of the line.'''
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
    '''[INTERNAL] Tick the axis from (x,y) to (x2,y2).  Should be constant along x,y to get tick marks.
    notick -- [T/F] does not print out the tickmarks
    reverse -- [T/F]reverses the text for top/right axes
    ndivisions -- [N] number of times to subdivide up the range
    ticklen -- [Fraction] the fraction of the range that becomes the length of the ticks'''
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
    if not notext: self.text(x2,y2,"%.1f"%(value[1]), rotate=rotate, reverse=reverse)
    if colored: self._stroke()

  def grid(self, corner, gcorner, grange, gscale, 
            tickint=1.0, # every value in
            ticklen=0.1, #percent
            ndivisions=4, # power
            axiscolor=0.1,
            gridcolor=0.9):
    ''' Builds a grid starting on the page at corner, with grid corner  (gcorner)
    with range (grange)  all should be in inches and have (x,y) '''
    def _gridline(i,a,b,z):
      '''make a nice line from a to b at z.  i == 0 a -> b along x, i == 1 : along y'''
      if i == 0:
        self.line(a,z,b,z)
        # self.circle(a,z,.05,color=(0,1,1))
        # self.circle(b,z,.05,color=(0,1,1))
      else:
        self.line(z,a,z,b)
        # self.circle(z,a,.05,color=(0,1,0))
        # self.circle(z,b,.05,color=(0,1,0))

    
    self.circle(corner[0],corner[1], 0.2)
    # i -- axis, idea: start at left bottom, and count upwards to grange adding ticks and lines

    # major tick marks
    colored = self.setcolor(gridcolor)
    for i,(c,gl,gr) in enumerate(zip(corner,gcorner,grange)):
      gh = gr-gl
      major = arange(0,floor(gh)-ceil(gl), tickint) + (ceil(gl)-gl)
      print gl, gh, major
      for m in major:
        _gridline(i,c,c+gscale*gr,corner[i-1]+gscale*m)
    if colored : self._stroke()

    for i,(c,gl,gr) in enumerate(zip(corner,gcorner,grange)):
      gh = gr-gl
      minor = arange(floor(gl),ceil(gh), 1.0/pow(2,ndivisions))
      _gridline(i,c,c+gscale*gr,corner[1-i])

    
    print 'done'


  def oldgrid(self, axiscolor=0.1, gridcolor=0.9):
    '''Makes a nice graph on the postscript.
    [FIXME] need to generalize this to have negative and positive grids
    axiscolor -- [COLOR] sets the color of the x,y axis to be some color
    gridcolor -- [COLOR] sets the background grid color.'''
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
    '''Plot a connected line for each (x,y) in (xarr,yarr).
    color -- [COLOR] color of the line
    width -- [INCHES] width of the line'''
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