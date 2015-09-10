#!/usr/bin/env python
# tool.py : Parses a gcode file
# [2012.07.31] Mendez

# Parse a series of g code moves represented by a Gcode object into a much less general however much more easily manipulated toolpath format called Tool
# of specific interest is the class IndexDict() which can be found in util
# the index dict is used as an intermediate datastructure between the GCODE instance input and the Tool instance output which is actially composed of a list of IndexDicts

'''
#For EXAMPLE here self is a "TOOL" and has a simple orgainztion of relevant data
#Item is an IndxDict() instance from the Tool() instance called self
for i,item in enumerate(self):
    x,y,z,cmd = item[0:4]
'''
# [2015.08.15] Erickstad

import re,sys,math
from pprint import pprint
from string import Template
from copy import deepcopy


from clint.textui import colored, puts, indent, progress
from util import error, distance, IndexDict
from mill import Mill

#needed for zcorrect to use correction surface features
from correction_surface import CorrectionSurface

AXIS='XYZIJ'

TEMPLATE='''(Built with python and a dash of Mendez)
(GCODE Start nCommands:${ncommand} npaths:${nmill})
${units}
${movement}
${gcode}
(GCODE End)
${footer}'''


# def nan():
#   ''' only used for _old_build'''
#   return [float('nan')]*3
def origin():
  return IndexDict.setorigin()
  # return [0.0]*3

# Moves and the sort
def noop(self,m=None,t=None):
  pass

def home(self,m=None,t=None):
  self.append(origin())
  # self.append(origin()+[0]) #origin

def inch(self,m=None,t=None):
  self.units = 'inch'

def mm(self,m=None,t=None):
  self.unis = 'mm'

def absolute(self,m=None,t=None):
  self.abs = True

def relative(self,m=None,t=None):
  self.abs = False

def move(self,m,cmd, z=None):
  '''Moves to location. if NaN, use previous. handles rel/abs'''
  for i,key in enumerate(m):
    if not math.isnan(m[i]):
      m[i] = convert(self,m[i])
    else:
      m[i] = self[-1][i]
  m[3] = cmd
  if z: m[2] = z
  self.append(m)

  # loc = convert(self,m) # ensure everything is in inches
  # loc = [x if not math.isnan(x) else self[-1][i] for i,x in enumerate(loc.values())] # clean NAN
  # if not self.abs: loc += self[-1][:] # rel/abs
  # loc.append(t)
  # self.append(loc)

def convert(self,m):
  if self.units == 'mm':
    m = [x*25.4 for x in m]
  return m

def millMove(self, next, height):
  '''Move the toolbit to the next mill location'''
  last = self[-1]
  move(self, IndexDict(last), 1, z=height) # lift off of board; move at feed rate in case we're drilling.  Ideally we'd only move at feed rate for the liftoff if we were drilling and not if we're milling, but the current structure of the code makes it rather tricky to find that out in a robust way, so for now just defaulting to always liftoff ad feed rate, which should be safe and have negligible effects on total job time
  move(self, IndexDict(last), 0, z=height) # hack for old drawing code: lift off to same position at move speed so drawing code will put in move operations
  move(self, IndexDict(next), 0, z=height) # Move to next pos

def circle(self,m,t):
  move(self, m, t)
  # FIXME

'''DICTIONARY OF FUNCTIONS'''
'''SEE DEFINITIONS ABOVE'''
GCMD = {0:  move,
        1:  move,
        2:  circle,
        3:  circle,
        4:  noop,
        17: noop, #xyplane
        20: inch,
        21: mm,
        54: noop, # Word Coords
        90: absolute,
        91: relative,
        94: noop, #FeedRate/minute
        }


class Tool(list):
  def __init__(self, gcode=None):
    ''' By default the machine starts in absolute with "mm" as the units.
    Go to the home location and then add moves'''
    self.abs = True
    self.units = 'inch'
    self.mills = []
    home(self)
    if gcode: self.build(gcode)

  def __repr__(self):
    '''Slightly more information when you print out this object.'''
    return '%s() : %i locations, units: %s'%(self.__class__.__name__, len(self),self.units)


  def build(self, gcode):
    '''New gCode that uses the indexedDict'''
    puts(colored.blue('Building Toolpath:'))
    for i,line in enumerate(progress.bar(gcode)):
    # for i,line in enumerate(gcode):
      if 'G' in line: # only handle the gcodes
        # Get the G code number assign it to cmd
        # for human readablitiy cmd should be changes to g_command_number
        # or somehting like that
        # however notice that it is hardcoded as a  dict key as well
        '''copy over the relevant data x y z i j index and g_command_number'''
        '''To an indexdict named move with the name attribute set to the string "move" '''
        cmd = line['G']
        move = IndexDict(name='move')
        for j,x in enumerate(AXIS):
          if x in line: move[x] = line[x]
        move['cmd'] = cmd
        move['index'] = line['index']

        try:
          fcn = GCMD[cmd]
          move.name = 'cmd[% 2i]'%cmd
          # Try using the indexdict instance as info for the next coordinates to be attached to the toolpath
          # by way of the function fcn selcted from the dict of functions GCMD above
          fcn(self, move, cmd)
        except KeyError:
          # raise
          error('Missing command in GCMD: %d(%s)'%(cmd, line))

  # def _old_build(self, gcode, addIndex=False):
  #   '''Parse gCode listing to follow a bit location
  #   addindex [false] : adds the index to the last spot so that we can update and the push back'''
  #   puts(colored.blue('Building Toolpath:'))

  #   # for each line of the gcode, accumulate the location of a toolbit
  #   for i,line in enumerate(progress.bar(gcode)):
  #   # for i,line in enumerate(gcode):

  #     move = nan()
  #     if 'G' in line:
  #       t = line['G']  # type of command
  #       for j,x in enumerate(AXIS): # grab all changes
  #         if x in line: move[j] = line[x]
  #       # Apply changes to the object
  #       try:
  #         fcn = GCMD[t]
  #         fcn(self,move,t)
  #         if addIndex and (t in [0,1]): self[-1].append(line['index'])
  #       except KeyError:
  #         error('Missing command in GCMD: %d(%s)'%(t, line))

  def boundBox(self):
    '''Returns the bounding box [[xmin,xmax],[ymin,ymax],[zmin,zmax]]
    for the toolpath'''
    box = [[0.,0.],[0.,0.],[0.,0.]]
    # for each element of the toolpath
    for item in self:
      # for each coordinate "ax"
      for i,ax in enumerate(item):
        # print i,ax
        if item[ax] < box[i][0]: box[i][0] = item[ax]
        if item[ax] > box[i][1]: box[i][1] = item[ax]
        # if j == 2 : sys.exit()
    # if afterwards the box has no dimensions throw an error
    if box == [[0.,0.],[0.,0.],[0.,0.]]:
      print 'Bounding box has no size; toolpath may not have been parsed correctly'
    return box

  def offset(self, offset):
    '''offset the toolpath by some offset=x,y,z
    this needs to be cleaned up'''
    for item in self:
      for i,ax in enumerate(item):
        if i == 0:
          item[ax] -= offset[0]
        elif i == 1:
          item[ax] -= offset[1]
        elif i == 2:
          item[ax] -= offset[2]


  def rotate(self, angle):
    '''rotate by some angle'''
    rad = math.radians(angle)
    for item in self:
      # 90 deg
      # item[0],item[1] = -item[1], item[0]
      a = math.cos(rad)*item[0] - math.sin(rad)*item[1]
      b = math.sin(rad)*item[0] + math.cos(rad)*item[1]
      item[0], item[1] = a,b


  # def _badclean(self):
  #   '''A temporary fix to check the bike program'''
  #   loc=[0.0,0.0,0.0]
  #   for item in self:
  #     # if distance(item[0:3],loc) > 3:
  #     if max(item) > 10:
  #       print 'xxx Removed: %s'%(str(item))
  #       self.remove(item)
  #     else:
  #       loc = item


  def uniq(self):
    '''make the toolpath uniq -- reverse + pop does it correctly '''
    for i in reversed(range(1,len(self))):
      if self[i] == self[i-1]:
        self.pop(i)

  def length(self):
    '''get the length of a toolpath'''
    length = 0.0
    for i in range(len(self)-1):
      length += distance(self[i],self[i+1])
    return length

  def millLength(self):
    '''Gets the length of the self.mills part'''
    length = 0.0
    for mill in self.mills:
      length += mill.length()
    return length

  # def _old_groupMills(self):
  #   '''Groups the toolpath into individual mills'''
  #   puts(colored.blue('Grouping paths:'))

  #   mill = Mill();
  #   for x,y,z,t in progress.bar(self):
  #   # for i,[x,y,z,t]  in enumerate(self):
  #     if t == 1:
  #       mill.append([x,y,z])
  #     else:
  #       if len(mill) > 0:
  #         self.mills.append(mill)
  #         mill = Mill() # ready for more mills
  def groupMills(self):
    '''Groups the toolpath into individual mills'''
    puts(colored.blue('Grouping paths:'))

    mill = Mill();
    for item in progress.bar(self):
      if item.cmd in (1,2,3):
        mill.append(item)
      else:
        if len(mill) > 0:
          self.mills.append(mill)
          mill = Mill() # ready for more mills

    # and get the last one!
    if len(mill) > 0: self.mills.append(mill)

  def uniqMills(self):
    '''Uniqify the points in each of the millings'''
    for mill in self.mills:
      mill.uniqify()

  def setMillHeight(self, millHeight=None, drillDepth=None):
    '''Sets the Mill height, for spot drilling
        millHeight and drillHeight in MILs'''
    for mill in self.mills:
      if mill.isDrill():
        mill.setZ(drillDepth/1000.)
      else:
        mill.setZ(millHeight/1000.)

  def getNextMill(self, X):
    '''Gets the next next mill to point X, using just the mill start point.'''
    distances = [distance(mill[0],X) for mill in self.mills]
    index = distances.index(min(distances))
    # print '%i : % 4.0f mil'%(index, min(distances)*1000.0)
    return self.mills.pop(index)

  def getClosestMill(self, X):
    ''' Improved getNextMill, optimizes the location to start in the mill
    Now checks to see if the starting and ending point are close so can be
    reordered.  This ends up being a traveling salesman problem, so
    keeping with this solution is easiest. '''
    # get the path with a point that is closest to X
    distances = [distance(mill.closestLocation(X),X) for mill in self.mills]
    index = distances.index(min(distances))
    mill = self.mills.pop(index)

    # reorder the path so that the start is close to x
    mill.reorderLocations(X)
    return mill




  def reTool(self, moveHeight=None):
    '''Rebuild the toolpath using the Mills
    moveHeight is in MILLs and is the height at which the machine moves'''
    # self[:] = list() # Remove old toolpath !!!
    while len(self)>0: self.pop()
    home(self)
    self.abs=True
    self.units='inch'

    heightInches = moveHeight/1000.

    puts(colored.blue('Retooling path from mills:'))
    for mill in progress.bar(self.mills):
      # start by moving to the starting location of the mill
      millMove(self, mill[0], heightInches)

      for i,x in enumerate(mill):
        # mill connecting each location
        move(self, x, 1) # it says move, but cmd == 1 so it is a mill

    # ok done, so move to the  to origin
    millMove(self, origin(), heightInches)


  def buildGcode(self):
    '''This returns a string with the GCODE in it.'''
    lines = []
    iMill = 1
    # for i,[x,y,z,t] in enumerate(self):
    for i,item in enumerate(self):
      x,y,z,cmd = item[0:4]

      # OK this is a crappy hack to ensure that we put a nice little name before  each mill.
      # so basically we need z>0, this one be a move and the next one be a mill
      # and then we write a nice message
      if ([l[3] for l in self[i:i+2]] == [0,1] and z > 0):
        lines.append('\n(Mill: %04i)'%(iMill))
        iMill += 1
      lines.append('G%02i   X%.3f Y%.3f Z%.3f'%(cmd,x,y,z))
    gcode ='\n'.join(lines)
    params = dict(units='G20' if (self.units == 'inch') else 'G21',
                  movement='G90' if self.abs else 'G91',
                  gcode=gcode,
                  nmill=iMill,
                  ncommand=len(self),
                  footer='')
    return Template(TEMPLATE).substitute(params)


  #### some commands to move / copy and otherwise change the gcode.
  def move(self,loc):
    '''Moves the toolpath from (0,0) to (loc[0],loc[1])'''
    '''Moves the toolpath from (x_n,y_n) to (x_n+loc[0],y_n+loc[1]) for all n?'''
    for item in self:
      for i,x in enumerate(loc):
        item[i] += x

  def zcorrect(self, correction_surface):
    #correct the z position of the points on the tool path
    for item in self:
        item[2] += correction_surface.estimate_surface_z_at_pozition(item[0],item[1])
