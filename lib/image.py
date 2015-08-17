#!/usr/bin/env python
# image.py : a nice image library
# [2012.08.21] - Mendez
import os, re, sys
from datetime import datetime
from random import uniform
from clint.textui import puts, colored, progress
from lib.util import deltaTime, error, distance

# from math import pi
from numpy import arange, floor, ceil, arctan2, pi, sqrt, cos, sin
from pyx import *

unit.set(defaultunit="inch")
text.set(mode="latex")
text.preamble(r"\usepackage[scaled]{helvet}\renewcommand{\rmdefault}{phv}\renewcommand{\sfdefault}{phv}")

DELTA_CURVE_IN = 0.002


def update_path(path, tool, cmd):
  '''update function to simplify below'''
  tmp = [tool.x,tool.y]

  # for arcs we need to know some special bits (in Mendez speak circa 2013 bits cn refer to any noun)
  # (in this case he is telling you that arcs used I and J variables to plot thier path)
  if cmd in (2,3):
     tmp.extend([tool['I'],tool['J'],cmd])

  # make sure that we only add new points / or if path is empty
  if len(path) < 1 or tmp != path[-1] :
    path.append(tmp)

  return cmd, path


class Image(object):
  def __init__(self, filename=None,
               gridscale=1.0,
               gridsize=[[0.0,1.0],[0.0,1.0]],
               pagesize=(7.5,4),  # width,height [in]
               embiggen=0.10, # percent to add to size
               pagemargin=0.5):
    ''' Image Canvas with milling functions.
    gridscale : [Float] multiplication factor for grid size
    gridsize  : [Inches] The physical space to span. [[xmin,xmax],[ymin,ymax]]
    pagesize  : [inches] Can be (width,height) or 'letter','letter*', 'A3',A4'
                 Append * to get landscape.
    pagemargin : [inches] Top, right, bottom, left margins.'''
    if filename:
      self.filename = os.path.expanduser(os.path.expandvars(filename))
    else:
       self.filename = None

    delta = [[x[0], x[1], abs(x[1] - x[0])] for x in gridsize]
    grid = [[d[0] - embiggen*d[2], d[1] + embiggen*d[2]] for d in delta]

    self.gridsize = gridsize
    self.pagesize = pagesize
    self.pagemargin = pagemargin

    # setup ticks every so often
    ticks =      ['1',            '1/2', '1/4', '1/8', '1/16']
    gridcolors = [color.cmyk.Grey, None, None,  None,  None]
    ticklen =    [0.15,            0.1,  0.05,  0.025, 0.02]

    parter = graph.axis.parter.linear(ticks, labeldists=[1])
    painter = graph.axis.painter.regular(gridattrs=[attr.changelist(gridcolors)],
                                         # outerticklength=attr.changelist(ticklen),
                                         innerticklength=attr.changelist(ticklen) )
    x = graph.axis.linear(min=grid[0][0], max=grid[0][1],
                          painter=painter, parter=parter,
                          title='X [inch]')
    y = graph.axis.linear(min=grid[1][0], max=grid[1][1],
                          painter=painter, parter=parter,
                          title='Y [inch]')

    print("Ratio: %f"%(delta[0][2]/delta[1][2]))
    self.g = graph.graphxy(x=x, y=y,width=pagesize[0], ratio=delta[0][2]/delta[1][2])

    self.c = canvas.canvas()
    self.c.insert(self.g, [trafo.rotate(-90)])
    # self.d = document.document(document.page(self.c, margin=self.pagemargin))

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
    x = abs(gridsize[0][0]-gridsize[0][1])
    y = abs(gridsize[1][1]-gridsize[1][0])
    print 'xxxx', gridsize, 'yyyy'

    gx,gy = self.g.vpos(0.95,-0.05)
    t = self.c.text(gx,gy, 'Bound[in]: (%0.1f,%0.1f)'%(x,y),
                    [text.halign.boxright, text.valign.top])
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
    puts(colored.green('Writing : %s'%fname))
    # self.d.writetofile(fname)
    if '.pdf' in fname:
      self.c.writePDFfile(fname)
    else:
      self.c.writeEPSfile(fname)


  def showall(self,tool):
    ''' Grab everything and show it to the user [DEBUG]'''
    p=[]
    for i, t in enumerate(tool): p.append([t.x,t.y])
    xarr,yarr = zip(*p)
    self.mill(xarr,yarr, color=color.rgb.green)

  def process(self,tool):
    '''Mill out a toolpath.  groups together mills, moves, and
    drill, and then plots them together'''
    puts(colored.blue('Processing toolpath for drawing:'))

    # self.showall(tool)

    # we assume that we are starting with a g0x0y0z0
    last_cmd = 0
    path = [] # currently working things
    # mil,mov,dri,arc = [],[],[],[]
    output = dict(mill = [self.mill],
                  move = [self.move],
                  drill= [self.drill],
                  arc  = [self.arc],
                 )

    for i,t in enumerate(progress.bar(tool)):
    # for i,t in enumerate(tool):
      cmd = t.cmd

      # DEBUG  --  there are some oddly large jumps
      # if len(path) > 1:
      #   d = distance(path[-1][0:2],[t.x,t.y])
      #   if d > 1:
      #     puts(colored.red('Distance: %f at index: %d'%(d,t['index'])))
      #     print

      # If we are still doing the same op as last time, append to path
      if cmd == last_cmd:
        last_cmd, path = update_path(path, t, cmd)

      # if we are doing something different or we are done:
      if cmd != last_cmd or i == len(tool)-1:
        # finish each line with a Null Circles are special
        path.append([None]*len(path[-1]))

        # if   last_cmd == 1 and len(path) == 2 : dri.extend(path)
        # elif last_cmd == 0                    : mov.extend(path)
        # elif last_cmd == 1                    : mil.extend(path)
        # elif last_cmd in (2,3)                : arc.extend(path)
        if   last_cmd == 1 and len(path) == 2 : output['drill'].extend(path)
        elif last_cmd == 0                    : output['move'].extend(path)
        elif last_cmd == 1                    : output['mill'].extend(path)
        elif last_cmd in (2,3)                : output['arc'].extend(path)

        # Prep for next path.  if we are starting a arc
        # the path needs to know where we are starting
        # x,y,i,j,cmd
        if cmd in (2,3):
          nextpath = [ [path[-2][0],path[-2][1],None,None,cmd] ]
        else:
          nextpath = []

        # ok done with plotting, now get ready for next path
        # dont forget about getting the current point before changing to next
        last_cmd, path = update_path(nextpath, t, cmd) # start with nothing

    # Ok plot everything, lines will not be connected between nulls
    # if len(mil) > 0 : self.mill(zip(*mil)[0], zip(*mil)[1])
    # # if len(arc) > 0 : self.arc(zip(*arc)[0], zip(*arc)[1])
    # if len(arc) > 0 :
    #   x,y = self._interpArc(*zip(*arc))
    #   self.arc(x,y)

    # if len(mov) > 0 : self.move(zip(*mov)[0], zip(*mov)[1])
    # if len(dri) > 0 : self.drill(zip(*dri)[0], zip(*dri)[1])
    for key in output:
      paths = output[key]
      fcn = paths.pop(0)

      if len(paths) > 0:
        if key == 'arc':
          # print paths
          x,y = self._interpArc(*zip(*paths))
        else:
          x,y = zip(*paths)
        fcn(x,y)



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
            color=color.gray(0.45),
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

  def arc(self, xarr,yarr,
             color=color.cmyk.Cyan,
             width=0.010):
    '''Make a nice arc'''
    w = self._convertwidth(width)
    self.g.plot(graph.data.points(zip(xarr, yarr), x=1, y=2),
                 [graph.style.line([w,color])] )


  def _interpArc(self, xarr, yarr, iarr, jarr, cmd):
    x,y = [],[]


    for i in range(1,len(cmd)-1):
      if cmd[i] is None or cmd[i-1] is None:
        continue
      print i, xarr[i-1],yarr[i-1]
      print '   ', xarr[i], yarr[i], iarr[i], jarr[i], cmd[i]

      center = [xarr[i-1]+iarr[i], yarr[i-1]+jarr[i]]
      a = [xarr[i-1]-center[0], yarr[i-1]-center[1]]
      b = [xarr[i]-center[0], yarr[i]-center[1]]

      if cmd[i] == 2:
        angle = [arctan2(b[1],b[0]),arctan2(a[1],a[0])]
      else:
        angle = [arctan2(a[1],a[0]),arctan2(b[1],b[0])]
      if angle[1] <= angle[0]:
        angle[1] += 2*pi
      ang = angle[1] - angle[0]

      radius = sqrt(pow(a[0],2)+pow(a[1],2))
      length = radius*ang

      delta = DELTA_CURVE_IN
      steps = length/delta

      for j in arange(0,steps):
        k = j if cmd[i]==2 else steps-j
        x.append( center[0] + radius*cos(angle[0] + ang*float(k)/steps) )
        y.append( center[1] + radius*sin(angle[0] + ang*float(k)/steps) )

      # done so append none to seperate lines
      x.append(None)
      y.append(None)
    return x,y
