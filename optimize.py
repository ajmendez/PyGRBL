#!/usr/bin/env python
# optimize.py
# reads and optimizes an gcode file.
#  python optimize.py file.nc        # optimized: file_opt.nc
# [2011.12.25] Mendez's Optimizer

import sys, getopt, os
from toolpath import ToolPath, distance, getclosestindex



WARN = ['\033[91m', '\033[0m']
MOVE_DEPTH  =  0.020
MILL_DEPTH  = -0.004
DRILL_DEPTH = -0.063
MOVE = 'G00'
MILL = 'G01'
GCODE_BEGIN = '''G20
G90
G00 X0.00 Y0.00 Z0.00
M03
M04 P1.0 (PAUSE TO CHECK IF OK)
'''
GCODE_BETWEEN=['%s Z%6.4f'%(MOVE,MOVE_DEPTH),
               '%s Z%6.4f'%(MILL, MILL_DEPTH),
               '%s Z%6.4f'%(MILL, DRILL_DEPTH)]
GCODE_END='''G00 Z0.500
G00 X0.00 Y0.00 Z0.500
G00 X0.00 Y0.00 Z0.000
'''
GCODE_MOVE = '%s X'%(MOVE)
GCODE_MILL = '%s X'%(MILL)

class Paths(list):
  def totallength(self):
    length = 0.0
    for path in self:
      if path.method == MOVE:
        length += path.totallength()
    return length
  
  def getpath(self,x=0.0, y=0.0):
    return self.getclosestpath(x,y,shuffle=False)
  
  def getclosestpath(self,x=0.0,y=0.0, shuffle=True):
    '''pops the closest path from the list'''
    location = [item.startingpoint(x,y, shuffle=shuffle) for item in self]
    index = getclosestindex(location,x,y)
    return (location[index], self.pop(index))
  
  # def getrecursepath(self,x,y,z, path=None, recurse=0, maxrecurse = 4):
  #   '''recursively search for the shortest path'''
  #   if path is None: 
  #     (x1,y1,z1), path = self.getclosestpath(self,x,y)
  #   if len(self) == 0 or recurse == maxrecurse:
  #     return (path.startingpoint(), path)
  #   
  #   # So we should operate on path, we are at x,y and we want to find the path which is closest
  #   
  #   distances = [distance(x1,y1, ) for x,y,z in path.previous]
  #   mindistance = min(distances)
  #   l = path.previous[distances.index(mindistance)]
  #   lnew, path = self.getrecursepath(l[0], l[1], l[1])
  #   self.append(path)
  #   return blah
    
  def getbetterpath(self, x, y):
    l_start, path  = self.getclosestpath(x,y)
    l_end = path.endingpoint()
    if len(self) == 0: return (l_start, path)
    l_next, path2 = self.getclosestpath(l_end[0],l_end[1])
    l_better = path.startingpoint2(x,y, l_next[0], l_next[1])
    self.append(path2)
    return (l_better, path) 
  
  def togcode(self):
    out = []
    out.extend(GCODE_BEGIN.splitlines())
    for item in self:
      if item.method == MOVE: i=0
      elif item.method == MILL: i=1
      else: self.error("undefined method")
      out.extend(GCODE_BETWEEN[i].splitlines())
      out.extend(item.pathgcode(simple=True))
    out.extend(GCODE_END.splitlines())
    return out
  
  @classmethod
  def NewMovePath(self, x1,y1, x2,y2):
    '''Oh it is simple, just move since we have already lifted'''
    thispath = ToolPath(x=x1,y=y1,method=MOVE)
    thispath.absolute(x=x2, y=y2)
    return thispath




class Optimize(object):
  def __init__(self, argv=None):
    '''start the path'''
    self.args, self.debug = self.getargs(argv)
    self.main()
  
  def main(self):
    self.load_file()
    self.parse_raw()
    self.optimize_rawpath()
    self.write_optimized()
  
  def checkattr(self, attr, message, negate=False, error=False):
    ''' Errors if attr is False or not an attribute of this class.'''
    if type(attr) == str:
      if not hasattr(self, attr): error=True
    elif type(attr) == bool:
      if not attr: error = True
    if not (error == negate):
      self.error("%s not found -- %s"%(attr, message))
  def checknotattr(self, attr, message, negate=True):
    self.checkattr(attr, message, negate=negate)
  
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
    self.checkattr(len(self.args) == 2, "Please load a file by %s [-d] inputfile.nc"%(self.args[0]))
    with open(self.args[1], 'r') as f: self.raw = f.readlines()
  
  # def parse_gcode(self, line):
  #   '''Lets start with just some x,y locations, add z later'''
  #   g, x, y, z = -1, -1, -1, -1
  #   tmp = line.split()
  #   for t in tmp:
  #     if   'X' in t: x = float(t.strip('X'))
  #     elif 'Y' in t: y = float(t.strip('Y'))
  #     elif 'Z' in t: z = float(t.strip('Z'))
  #     elif 'G' in t: g = float(t.strip('G'))
  #   return (g,x,y,z)
  def parse_gcode(self, line):
    '''Parse each line a bit better. parses G,x,y,z as floats'''
    tmp = line.split()
    out = {}
    for item in ['G','X','Y','Z']: out[item] = None
    for t in tmp:
      for item in out:
        if item in t: 
          out[item] = float(t.strip(item))
    return out
    
  def parse_raw(self):
    '''Parse the raw gcode for a 2d plane'''
    self.checkattr('raw',"Please load some data into self.raw before running")
    self.checknotattr('rawpaths',"Already Processed paths, please check")
    
    self.rawpaths = Paths()
    i=0 # someone please tell me a pythonic way of doing this
    while i < len(self.raw):
      line = self.raw[i]
      start = True
      # For each of the mill paths
      while GCODE_MILL in line:
        out = self.parse_gcode(line)
        # if this is a new mill, then start a milling path, else start a move.
        if start: 
          millpath = ToolPath(x=out['X'], 
                              y=out['Y'], 
                              z=MILL_DEPTH, 
                              method=MILL)
          start = False
        else:
          millpath = ToolPath(x=out['X'], 
                              y=out['Y'], 
                              z=MILL_DEPTH, 
                              method=MOVE)
        i += 1
        line = self.raw[i]
      if start is False:
        self.rawpaths.append(millpath)
      i += 1
    self.rawpathlength = self.rawpaths.totallength()
      
  
  def optimize_rawpath(self, x=0.0, y=0.0, z=0.0, method='xxx',path=Paths):
    '''Find the path with the smallest travel length'''
    self.orderedpaths = path()
    
    while len(self.rawpaths) > 0:
      if method ==  'closest': (x1,y1,z1), closestpath = self.rawpaths.getclosestpath(x,y)
      elif method == 'better': (x1,y1,z1), closestpath = self.rawpaths.getbetterpath(x,y)
      # elif method == 'recurse': (x1,y1,z), closestpath = self.rawpaths.getrecursepath(x,y)
      else: (x1,y1,z1), closestpath = self.rawpaths.getpath(x,y)
      
      if not hasattr(self.orderedpaths,'drill'):
        closestpath.absolute(x1,y1,z1)
      mpath = path().NewMovePath(x,y, x1,y1)
      self.orderedpaths.append(mpath) 
      if not hasattr(self.orderedpaths,'drill'):
        self.orderedpaths.append(closestpath)
      x2,y2,z2 = closestpath.endingpoint()
      x,y,z = x2,y2,z2
    self.orderedpathlength = self.orderedpaths.totallength()
  
  def write_optimized(self):
    self.checkattr('orderedpaths', "Ordered Path Needed")
    outfile = '_opt'.join(os.path.splitext(self.args[1]))
    self.write("Writing to file: %s"%outfile)
    self.write("WRONG LENGTHS: Raw Pathlength | Full Path Length: %4.2f | %4.2f "%(self.rawpathlength,
                                                           self.orderedpathlength))
    gcode = self.orderedpaths.togcode()
    with open(outfile,'w') as f:
      for item in gcode: f.write(item+'\n')
  
if __name__ == "__main__":
  O = Optimize()
  sys.exit()
  






