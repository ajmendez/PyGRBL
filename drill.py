#!/usr/bin/env python
# drill.py
# reads and optimizes an drill file
#  python optimize.py drill.nc        # optimized: file_opt.nc
# [2011.12.25] Mendez's drill fun

import sys, getopt, os
from toolpath import distance
from toolpath import Toolpath2 as ToolPath
from optimize import Optimize, Paths,  MILL,MOVE, GCODE_MILL,GCODE_BEGIN,GCODE_BETWEEN, GCODE_END


class DrillPaths(Paths):
  drill=True
  def togcode(self):
    out = []
    out.extend(GCODE_BEGIN.splitlines())
    for item in self:
      out.append(GCODE_BETWEEN[0]) # LIFT
      out.append('%s X%6.4f Y%6.4f'%(MOVE, item.x, item.y) ) # MOVE
      out.append(GCODE_BETWEEN[2]) # MILL
    
    out.extend(GCODE_END.splitlines())
    return out
  

class Drill(Optimize):
  def main(self):
    self.load_file()
    self.parse_drills()
    self.get_drillpath()
    self.optimize_rawpath(method='basic',path=DrillPaths)
    self.write_optimized()
    
  def parse_gcode(self, line):
    '''Better parse'''
    tmp = line.split()
    out = {}
    for item in ['G','X','Y','Z']: out[item] = None
    for t in tmp:
      for item in out:
        if item in t: 
          out[item] = float(t.strip(item))
    return out
    
  def parse_drills(self):
    self.rawdrill = ToolPath()
    while len(self.raw) > 0:
      line = self.raw.pop(0)
      out = self.parse_gcode(line)
      if out['G'] != None:
        self.rawdrill.absolute(g=out['G'],x=out['X'],y=out['Y'],z=out['Z'])
  
  def get_next(self, l, x, y):
    distances = [distance(x,y, x1,y1) for G,x1,y1,z in l]
    mindistance = min(distances)
    return l.pop(distances.index(mindistance))
  
  def get_drillpath(self,x=0.0, y=0.0):
    self.rawpaths = Paths()
    rawdrill = self.rawdrill
    
    while len(rawdrill) > 0:
      l = self.get_next(rawdrill,x,y)
      if l[0] == 1:
        g,x,y,z = l
        millpath = ToolPath(x=x, y=y, z=z,method=MOVE)
        self.rawpaths.append(millpath)
        
        
    
if __name__ == "__main__":
  D = Drill()
  sys.exit()
