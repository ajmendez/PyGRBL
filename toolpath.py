from math import sqrt
from numpy import median
from itertools import cycle

class ToolPath(object):
  def __init__(self, x=0.0, y=0.0, z=0.0, method=None, maxpoints=10000):
    self.maxpoints = maxpoints
    if not method: method = 'G01'
    self.x, self.y, self.z, self.method = x, y, z, method
    self.shiftmove = 0.1
    self.move = 0.01
    self.previous = []
    self.save()
  
  
  def absolute(self, x=None, y=None, z=None):
    if x: self.x = x
    if y: self.y = y 
    if z: self.z = z
    self.save()
  
  def relative(self, x=None, y=None, z=None):
    if x: self.x += x
    if y: self.y += y
    if z: self.z += z
    self.save()
  
  def __len__(self):
    return len(self.previous)
  
  
  def getdelta(self,array):
    x=array[:] # uhh?!
    delta=[]
    while len(x) > 1:
      item = x.pop()
      delta.append(self.distance(item[0],item[1], x[0][0],x[0][1]))
    return delta
  
  @classmethod
  def getclosestindex(self,location,x,y):
    distances = [self.distance(x,y, x2,y2) for x2,y2,z in location]
    mindistance = min(distances)
    index = distances.index(mindistance)
    if distances.count(mindistance) > 1: 
      print "check number of distance == mindistances"
    return index
    
  def startingpoint(self,x,y, shuffle=False):
    '''I might be able to shuffle the array to get closer points, but lazy for now
    This is also safer since I am not sure if there are lines rather than connected paths'''
    if shuffle:
      # there has to be a better way
      move = self.getdelta([self.previous[0], self.previous[-1]])
      distances = self.getdelta(self.previous)
      if move < median(distances):
        index = self.getclosestindex(self.previous,x,y)
        if index > 0:
          b = self.previous[index:]
          b.extend(self.previous[:index])
          self.previous = b
          print index
          print len(b), len(self.previous)
        # while index < len(self.previous):
        #   self.previous.insert(0, self.previous.pop())
    return self.previous[0]
  def endingpoint(self):
    return self.previous[-1]
  
  def center(self):
    '''returns the center of the path'''
    def centerind(thelist,ind):
      '''returns the center of a touple list'''
      def getind(item): return item[ind] 
      xs = map(getind,thelist)
      return sum(xs)/len(xs)
    x = centerind(self.previous,0)
    y = centerind(self.previous,1)
    return (x, y)
  
  
  
  def __str__(self):
    return "%8.4f %8.4f %8.4f"%(self.x, self.y, self.z)
  
  def gcode(self):
    return self.togcode(x=self.x,y=self.y, z=self.z, method=self.method)

  @classmethod
  def distance(self, x1,y1, x2,y2):
    return sqrt(pow(x2-x1,2)+pow(y2-y1,2))
  
  
  def togcode(self, x=None, y=None, z=None, method='G01', simple=False):
    if simple:
      return "%s X%6.4f Y%6.4f"%(method, x, y)
    else:
      return "%s X%6.4f Y%6.4f Z%6.4f"%(method, x, y, z)
  
  def pathgcode(self,method=None,simple=True):
    def simpleg(item):return self.togcode(item[0],item[1], method=method, simple=simple)
    return map(simpleg, self.previous)
    
  
  def save(self):
    v = (self.x, self.y, self.z)
    if len(self.previous) > self.maxpoints:
      self.pop(0)
    if len(self.previous) == 0 or self.previous[-1] != v:
      self.previous.append(v)