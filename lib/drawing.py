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

DELTA_CURVE_IN = 0.002


class Drawing(object):
  def __init__(self, filename=None, 
               pagemargin=0.1):
    ''' Image Canvas with milling functions. 
    pagemargin : [inches] Top, right, bottom, left margins.'''
    if filename:
      self.filename = os.path.expanduser(os.path.expandvars(filename))
    else:
      self.filename = None
    
    self.eps_header = "%!PS-Adobe-2.0 EPSF-2.0\n"
    self.ps = "gsave\n"
    self.ps += "{0} {0} translate\n".format(round(72*pagemargin))
    self.ps += "1 setlinecap 1 setlinejoin\n"
    self.ps += "0 0 moveto\n" # need a first point to get us started
    
    # bounding box
    self.margin = pagemargin;
    self.box = "1 0 0 setrgbcolor\n"
    self.box += "{0} {0} moveto\n".format(round(72*pagemargin))
    self.bounds = {'xmax': 0, 'ymax' : 0}


  def __enter__(self):
    '''with constructor :: generate a nice plot with a plot and axis'''
    return self
  def __exit__(self, type, value, traceback):
    '''with constructor finished -- close anything open.'''
    self.save()
    return isinstance(value, TypeError)

  def save(self,filename=None):
    if filename is None and self.filename is None: error("nowhere to save")
    fname = filename if self.filename is None else self.filename
    puts(colored.green('Writing : %s'%fname)) 
    # add the final bounding box to the postscript header
    self.apply_bounding_box()
    # combine everything together
    final_eps = self.eps_header + "\n" + self.box + "\n" + self.ps + "\ngrestore\n"
    with open(fname, "w") as eps_file:
      eps_file.write(final_eps)

  def apply_bounding_box(self):
    '''generate the postscript header and drawing commands for the bounding box'''
    xmax = (self.bounds['xmax']+self.margin*2)*72;
    ymax = (self.bounds['ymax']+self.margin*2)*72;
    self.eps_header += "%%BoundingBox: 0 0 {} {}\n".format(round(xmax), round(ymax))
    self.box += "{} {} lineto\n".format(round(72*self.margin), round((self.bounds['ymax']+self.margin)*72))
    self.box += "{} {} lineto\n".format(round((self.bounds['xmax']+self.margin)*72), round((self.bounds['ymax']+self.margin)*72))
    self.box += "{} {} lineto\n".format(round((self.bounds['xmax']+self.margin)*72), round(72*self.margin))
    self.box += "closepath stroke\n"

  def process(self,tool):
    '''Mill out a toolpath.  Currently etch-only - assume v-bit, i.e. depth=width and draw lines of the appropriate width to simulate etching'''
    puts(colored.blue('Processing toolpath for drawing:'))

    # we assume that we are starting with a g0x0y0z0
    last_cmd = 0
    last_z = 0

    for i,t in enumerate(progress.bar(tool)):
      cmd = t.cmd
      z = t.z
      if t.x > self.bounds['xmax']: self.bounds['xmax'] = t.x
      if t.y > self.bounds['ymax']: self.bounds['ymax'] = t.y

      # if we are doing something different or we are done:
      if cmd != last_cmd or last_z != z or i == len(tool)-1:
        if last_cmd == 0 or last_z >= 0:
          # draw thin grey lines for movement
          self.ps += "0.1 setlinewidth 0.5 0.5 0.5 setrgbcolor stroke\n"
        elif last_cmd == 1 :
          self.ps += "{} setlinewidth 0 1 0 setrgbcolor stroke\n".format(last_z*-72)
        elif last_cmd in (2,3) :
          puts(colored.red('um... don\'t know how to draw arcs yet!'))

        # move instead of drawing a line to the new point
        self.ps += "{0} {1} moveto\n{0} {1} lineto\n".format(t.x*72, t.y*72)
        # then update the last_cmd and last_z params
        last_cmd = cmd
      else:
        self.ps += "{} {} lineto\n".format(t.x*72, t.y*72)

      last_z = z

