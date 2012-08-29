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


def update_path(path, x,y,t):
  '''update function to simplify below'''
  tmp = [x,y]
  # make sure that we only add new points / or if path is empty
  if len(path) < 1 or tmp != path[-1] : path.append(tmp)
  return path


class Image(object):
  def __init__(self, filename=None, 
               gridscale=1.0,
               gridsize=[[0.0,1.0],[0.0,1.0]],
               pagesize=(5,4),  # width,height [in]
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
    grid = [[d[0] - embiggen*d[2],
             d[1] + embiggen*d[2]] for d in delta]

    self.gridsize = gridsize
    self.pagesize = pagesize
    unit.set(defaultunit="inch")
    self.g = graph.graphxy(width=pagesize[0], 
                           height=pagesize[1],
                           # xaxisat=0,yaxisat=0, 
                      x=graph.axis.linear(min=grid[0][0], 
                                          max=grid[0][1],
                                          title='X [inch]'),
                      y=graph.axis.linear(min=grid[1][0], 
                                          max=grid[1][1],
                                          title='Y [inch]'))

    # Grid lines
    for i, d in enumerate(delta):
      for x in range(int(d[0]),int(d[1])+1):
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
      self.g.writePDFfile(fname)
    else:
      self.g.writeEPSfile(fname)



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
    mil = []
    mov = []
    dri = []
    arc = []
    for i,t in enumerate(progress.bar(tool)):
    # for i,t in enumerate(tool):
      x,y,cmd = t.x,t.y,t['cmd']
      if cmd == last_cmd:
        path = update_path(path, x,y,cmd)
      elif cmd in (0,1,2):
        # ok so toolpath switched directive, so plot and then start next path
        # xarr,yarr = zip(*path) 
        # print "Last:%d, this:%d, length: %d"%(last_cmd, cmd, len(path))
        # a drill command is just a mill without moving around.
        if   last_cmd == 1 and len(path) < 3 : dri.extend(path)
        elif last_cmd == 0                   : mov.extend(path)
        elif last_cmd == 1                   : mil.extend(path)
        elif last_cmd == 2                   : arc.extend(path)
        # ok done with plotting, now get ready for next path
        # dont forget about getting the current point before changing to next
        path = update_path([], x,y,cmd) # start with nothing
        last_cmd = cmd
      else:
        print 'Please add cmd=[%d] to image.py'%(cmd)

    # print 'Move: %d, Mill: %d, Arc: %d, Drill: %d'%(len(mov),len(mil),len(arc),len(dri))
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
            color=color.cmyk.Gray,
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



