#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez 
import os, re, sys
from datetime import datetime
from random import uniform
from lib.clint.textui import puts, colored, progress
from lib.util import deltaTime, error

from numpy import arange, floor, ceil
from pyx import *

unit.set(defaultunit="inch")
text.set(mode="latex")
text.preamble(r"\usepackage[scaled]{helvet}\renewcommand{\rmdefault}{phv}\renewcommand{\sfdefault}{phv}")



def update_path(path, x,y,t):
  '''update function to simplify below'''
  tmp = [x,y]
  # make sure that we only add new points / or if path is empty
  if len(path) < 1 or tmp != path[-1] : path.append(tmp)
  return t, path


class Image(object):
  def __init__(self, filename=None, 
               gridscale=1.0,
               gridsize=[[0.0,1.0],[0.0,1.0]],
               pagesize=(7.5,4),  # width,height [in]
               embiggen=0.10, # percent to add to size
               pagemargin=(0.5,0.5,0.5,0.5)):
    ''' Image Canvas with milling functions. 
    gridscale : [Float] multiplication factor for grid size
    gridsize  : [Inches] The physical space to span. [[xmin,xmax],[ymin,ymax]]
    pagesize  : [inches] Can be (width,height) or 'letter','letter*', 'A3',A4'
                 Append * to get landscape.
    pagemargin : [inches] Top, right, bottom, left margins.'''
    self.filename = os.path.expanduser(os.path.expandvars(filename)) if filename else None
    delta = [[floor(x[0]), 
              ceil(x[1]), 
              abs(ceil(x[1]) - floor(x[0]))] for x in gridsize]
    delta = [[x[0], 
              x[1], 
              abs(x[1] - x[0])] for x in gridsize]

    grid = [[d[0] - embiggen*d[2],
             d[1] + embiggen*d[2]] for d in delta]

    self.gridsize = gridsize
    self.pagesize = pagesize


    
    # class axis(graph.axis.linear):
    #   def __init__(self, divisor=4, texter=graph.axis.texter.rational**kwargs)):
    #     axis.linear.__init__(self, divisor=divisor, texter=texter, **kwargs)

    ticks = ['1','1/2','1/4','1/8', '1/16']
    gridcolors = [color.cmyk.Grey,None,None,None,None]
    ticklen = [0.15, 0.1, 0.05, 0.025,0.02]
    parter = parter=graph.axis.parter.linear(ticks, labeldists=[1])
    painter = graph.axis.painter.regular(gridattrs=[attr.changelist(gridcolors)],
                                         # outerticklength=attr.changelist(ticklen), 
                                         innerticklength=attr.changelist(ticklen) )
    self.c = canvas.canvas()
    self.g = graph.graphxy(width=pagesize[0], 
                           # ratio=delta[1][2]/delta[0][2],
                           ratio=delta[0][2]/delta[1][2],
                           # margin=0.5*unit.w_inch,
                           # height=pagesize[1],
                           # xaxisat=0,yaxisat=0, 
                      x=graph.axis.linear(min=grid[0][0], 
                                          max=grid[0][1],
                                          painter=painter, parter=parter,
                                          title='X [inch]'),
                      y=graph.axis.linear(min=grid[1][0], 
                                          max=grid[1][1],
                                          painter=painter, parter=parter,
                                          title='Y [inch]'))
    self.c.insert(self.g)

    # Adds Origin in red
    for i, d in enumerate(delta):
      for x in range(0,1):
      # for x in range(int(d[0]),int(d[1])+1):

        c = color.cmyk.Red if x == 0 else color.cmyk.Gray
        w = style.linewidth.THIck if x == 0 else style.linewidth.THIN
        self.g.plot(graph.data.points(zip([x,x],grid[1-i][0:2]), x=i+1, y=2-i),
          [graph.style.line([w,c])])


    # bounding box
    self.g.plot(graph.data.points(zip([gridsize[0][j] for j in [0,1,1,0,0]],
                                      [gridsize[1][j] for j in [0,0,1,1,0]]), x=1, y=2), 
                [graph.style.line([color.cmyk.YellowOrange, 
                                   style.linewidth.THICK,
                                   style.linejoin.miter])])

    x = gridsize[0][0] if gridsize[0][0] < 0 else gridsize[0][1]
    y = gridsize[1][1] if gridsize[1][1] > 0 else gridsize[1][0]
    gx,gy = self.g.vpos(0.01,0.99)
    t = self.c.text(gx,gy, 'Bound[in]: (%0.1f,%0.1f)'%(x,y),[text.halign.boxleft, text.valign.top])
    tpath = t.bbox().enlarged(3*unit.x_pt).path()
    self.c.draw(tpath, [color.cmyk.White, deco.filled([color.cmyk.White])])
    self.c.insert(t)

    # center = t.marker("id")
    # self.g.stroke(path.circle(center[0], center[1], 0.125), [color.rgb.red])


  def __enter__(self):
    '''with constructor :: generate a nice plot with a plot and axis'''
    return self
  def __exit__(self, type, value, traceback):
    '''with constructor finished -- close anything open.'''
    self.save()
    return isinstance(value, TypeError)

  def save(self,filename=None, pdf=False):
    if filename is None and self.filename is None: error("nowhere to save")
    fname = filename if self.filename is None else self.filename
    puts(colored.blue('Writing : %s'%fname)) 
    if '.pdf' in fname:
      self.c.writePDFfile(fname)
    else:
      self.c.writeEPSfile(fname)



  def showall(self,tool):
    p=[]
    for i, t in enumerate(tool): p.append([t.x,t.y])
    xarr,yarr = zip(*p)
    self.mill(xarr,yarr, color=color.rgb.green)

  def process(self,tool):
    '''Mill out a toolpath.  groups together mills, moves, and 
    drill, and then plots them together'''
    # for i, t in enumerate(tool[0:20]): print i,t['cmd'],t.x, t.y
    puts(colored.blue('Processing toolpath for drawing:'))
    
    # self.showall(tool,color=color.cmyk.Gray)

    last_cmd = 0
    path = [] # currently working things
    mil,mov,dri,arc = [],[],[],[]

    # for i,t in enumerate(progress.bar(tool)):
    for i,t in enumerate(tool):
      x,y,cmd = t.x,t.y,t['cmd']

      if cmd == last_cmd:
        # If we are still doing the same op as last time, append to path
        last_cmd, path = update_path(path, x,y,cmd)

      if cmd != last_cmd or i == len(tool)-1:
        # if we are doing something different or we are done:
        path.append([None,None]) # add a null to the end of the path
        # drill is one move plus a null
        if   last_cmd == 1 and len(path) == 2 : dri.extend(path)
        elif last_cmd == 0                    : mov.extend(path)
        elif last_cmd == 1                    : mil.extend(path)
        elif last_cmd == 2                    : arc.extend(path)

        # ok done with plotting, now get ready for next path
        # dont forget about getting the current point before changing to next
        last_cmd, path = update_path([], x,y,cmd) # start with nothing

    # Ok plot everything, lines will not be connected between nulls
    if len(mil) > 0 : self.mill(zip(*mil)[0], zip(*mil)[1])
    if len(arc) > 0 : self.arc(zip(*arc)[0], zip(*arc)[1])
    if len(mov) > 0 : self.move(zip(*mov)[0], zip(*mov)[1])
    if len(dri) > 0 : self.drill(zip(*dri)[0], zip(*dri)[1])



  def _convertwidth(self,width):
    '''if is a float return the width in actual units or just return'''
    if isinstance(width,float):
      return style.linewidth(width*unit.w_inch)
    return width

   # the invidual plot commands
  def mill(self,xarr,yarr, 
            color=color.rgb.blue, 
            width=0.010): # in inches
    '''Mill an x,y array defaults to red and 10mil paths.'''
    w = self._convertwidth(width)
    self.g.plot(graph.data.points(zip(xarr, yarr), x=1, y=2),
            [graph.style.line([w, color])])

  def move(self,xarr,yarr, 
            color=color.gray(0.6),
            width=style.linewidth.thin):
    '''Moves the bit around (x,y) defaults to light blue and 1 point ('onepoint'),
    can pass a inch float as well.  '''
    w = self._convertwidth(width)
    
    self.g.plot(graph.data.points(zip(xarr, yarr), x=1, y=2),
            [graph.style.line([w, color])])

  def drill(self,x,y,
            r=0.032, 
            color=None, 
            outlinewidth=style.linewidth.thin,
            outlinecolor=color.rgb.blue):
    ''' A nice drill hole cross and defaults to 32mil holes'''
    w = self._convertwidth(outlinewidth)
    self.g.plot(graph.data.points(zip(x,y),x=1,y=2),
                  [graph.style.symbol(graph.style.symbol.circle, size=r*unit.w_inch,
                                      symbolattrs=[deco.stroked([w, outlinecolor])])])

  def arc(self,xarr,yarr, 
             color=color.cmyk.Red,
             width=0.020):
    '''Make a nice arc'''
    # temp hax
    self.mill(xarr,yarr, color=color, width=width)



