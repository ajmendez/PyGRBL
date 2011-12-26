class ToolPath(object):
  def __init__(self, x=0.0, y=0.0, z=0.0, maxpoints=10000):
    self.maxpoints = maxpoints
    self.x, self.y, self.z = x, y, z
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
  
  def __str__(self):
    return "%8.4f %8.4f %8.4f"%(self.x, self.y, self.z)
  
  def gcode(self, method='G01'):
    return "%s X%6.4f Y%6.4f Z%6.4f"%(method, self.x, self.y, self.z)
  
  def save(self):
    v = (self.x, self.y, self.z)
    if len(self.previous) > self.maxpoints:
      self.pop(0)
    if len(self.previous) == 0 or self.previous[-1] != v:
      self.previous.append(v)