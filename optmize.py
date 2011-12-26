#!/usr/bin/env python
# [2011.12.25] Mendez's Optimizer

import sys, getopt, os
from toolpath import ToolPath



WARN = ['\033[91m', '\033[0m']
MOVE_DEPTH =  0.02
MILL_DEPTH = -0.01
MOVE = 'G00'
MILL = 'G01'
GCODE_BEGIN = '''G20
G90
G00 X0.00 Y0.00 Z0.50
G00 X0.00 Y0.00 Z0.00
G00 Z0.5000 
M03
M04 P1.0 (PAUSE TO CHECK IF OK)
'''
GCODE_BETWEEN=['%s Z%6.4f'%(MOVE,MOVE_DEPTH),'%s Z%6.4f'%(MILL, MILL_DEPTH)]
GCODE_END='''G00 Z0.5000 
G00 X0.00 Y0.00 Z0.50
M05
M02'''
GCODE_MOVE = '%s X'%(MOVE)
GCODE_MILL = '%s X'%(MILL)

class Paths(list):
  def getclosestpath(self,x=0.0,y=0.0):
    '''pops the closest path from the list'''
    location = [item.startingpoint(x,y)[0:2] for item in self]
    distances = [item.distance(x,y, x2,y2) for x2,y2 in location]
    mindistance = min(distances)
    index = distances.index(mindistance)
    if distances.count(mindistance) > 1: 
      pass # I should error here
    return self.pop(index)
  
  @classmethod
  def movepath(self, x1,y1, x2,y2):
    '''Oh it is simple, just move since we have already lifted'''
    thispath = ToolPath(x=x1,y=y1,method=GCODE_MOVE)
    thispath.absolute(x=x2, y=y2)
    return thispath
  
  def togcode(self, method=None):
    out = []
    out.extend(GCODE_BEGIN.splitlines())
    for item in self:
      if item.method == GCODE_MOVE:
        out.extend(GCODE_BETWEEN[0].splitlines())
      elif item.method == GCODE_MILL:
        out.extend(GCODE_BETWEEN[1].splitlines())
      out.extend(item.pathgcode(GCODE_MILL, simple=True))
      
    out.extend(GCODE_END.splitlines())
    return out




class Optimize(object):
  def __init__(self, argv=None):
    '''start the path'''
    self.args, self.debug = self.getargs(argv)
    self.main()
  
  def main(self):
    self.load_file()
    self.parse_raw()
    self.optimize_rawpath('length')
    self.write_optimized()
  
  def checkattr(self, attr, message, negate=False, error=False):
    ''' Errors if attr is False or not an attribute of this class.'''
    if type(attr) == str:
      if not hasattr(self, attr): error=True
    elif type(attr) == bool:
      if not attr: error = True
    if not (error == negate):
      self.error("%s not found -- %s"%(attr, message))
  
  def write(self, message):
    print message
  def error(self, message, check=None):
    self.write("%s%s%s"%(WARN[0], message, WARN[1]))
    sys.exit()
  
  def getargs(self, argv=None, debug=False):
    '''Return the arguements and flags.'''
    if not argv: argv=sys.argv
    opts, args = getopt.gnu_getopt(argv[1:], 'hd')
    for opt, value in opts:
      if opt == '-h': print help
      if opt == '-d': debug=True
    args.insert(0, sys.argv[0])
    return (args, debug)
  
  def load_file(self):
    '''Loads a file, should at some point check the inputs'''
    self.checkattr(len(self.args) != 2, "Please load a file by %s [-d] inputfile.nc"%(self.args[0]), negate=True)
    with open(self.args[1], 'r') as f: self.raw = f.readlines()
  
  def parse_gcode(self, line):
    '''Lets start with just some x,y locations, add z later'''
    x, y = -1, -1
    tmp = line.split()
    for t in tmp:
      if   'X' in t: x = float(t.strip('X'))
      elif 'Y' in t: y = float(t.strip('Y'))
      # elif 'Z' in t: z = float(t.strip('Z'))
      # elif 'G' in t: g = float(t.strip('G'))
    return (x,y)
  
  def parse_raw(self):
    '''Parse the raw gcode for a 2d plane'''
    self.checkattr('raw',"Please load some data into self.raw before running")
    self.checkattr('rawpaths',"Already Processed paths, please check", negate=True)
    
    self.rawpaths = Paths()
    
    i=0 # someone please tell me a pythonic way of doing this
    while i < len(self.raw):
      line = self.raw[i]
      start = True
      # For each of the mill paths
      while GCODE_MILL in line:
        x,y = self.parse_gcode(line)
        if start: 
          millpath = ToolPath(x=x, y=y, z=MILL_DEPTH, method=GCODE_MILL)
          start = False
        else:
          millpath.absolute(x=x, y=y, z=MILL_DEPTH)
        i += 1
        line = self.raw[i]
      if start is False:
        self.rawpaths.append(millpath)
      i += 1
      
  def optimize_rawpath(self, method='length'):
    if method == 'length': self.optimize_length()
    else: self.error("Undefined optimize method")
  
  def optimize_length(self):
    '''Find the path with the smallest travel length'''
    x,y = 0.0, 0.0 # start at the origin
    self.orderedpaths = Paths()
    while len(self.rawpaths) > 0:
      closestpath = self.rawpaths.getclosestpath(x,y)
      x1,y1,z = closestpath.startingpoint(x,y, shuffle=True)
      # x1,y1,z = closestpath.startingpoint(x,y)
      movepath = Paths().movepath(x,y, x1,y1)
      self.orderedpaths.append(movepath) 
      self.orderedpaths.append(closestpath)
      x2,y2,z = closestpath.endingpoint()
      x,y = x2,y2
  
  def write_optimized(self):
    self.checkattr('orderedpaths', "Ordered Path Needed")
    outfile = '_opt'.join(os.path.splitext(self.args[1]))
    self.write("Writing to file: %s"%outfile)
    gcode = self.orderedpaths.togcode()
    with open(outfile,'w') as f:
      for item in gcode: f.write(item+'\n')
  
if __name__ == "__main__":
  O = Optimize()
  sys.exit()
  






