#!/usr/bin/env python

#this code should use a 2 dimensional array of z_positions
#the element 0,0 is 0 and all other elements are relative z positions
#there should also be a probe_step_x value and a probe_step_y value
#these define the distsnces between the points measured in the z_positions array

# as an example of using this code in ipython
# run -i zcorrect.py /home/mike/Desktop/greg.tap -z probe_test_2.out


#imports
import os, re, sys
from numpy import arange
# use argv in order to have options when using z correct as main function
from lib import argv
from lib.util import deltaTime
from datetime import datetime

#from lib.gparse import gparse
from lib.gcode import GCode
from lib.tool import Tool
from lib.grbl_status import GRBL_status
from lib.communicate import Communicate
from lib.correction_surface import CorrectionSurface
from clint.textui import puts, colored
import time, readline
import numpy as np
import re
import argparse

FILEENDING = '_mod' # file ending for optimized file.


EXTRAARGS = dict(ext=dict(args=['-z','--zsurface'],
                          type=str,
                          default='probe_test.out',
                          nargs = '?',
                          dest='z_surf',
                          help='''Specify the z zurface data file''') )


def zcorrect_file(gfile,surface_file_name = 'probe_test.out'):

    # Load the correction surface
    correction_surface = CorrectionSurface(surface_file_name)

    # keep track of time
    start = datetime.now()

    name = gfile if isinstance(gfile,str) else gfile.name
    puts(colored.blue('Z correcting the file: %s\n Started: %s'%(name,datetime.now())))

    # Load the gcode.
    gcode = GCode(gfile)
    #parse the Gcode
    gcode.parseAll()

    # start an empty list
    #out = []

    # need to get rid of use of 'loc'
    # loc = parse(args.move, getUnits=True) # only one move at a time.
    # puts(colored.blue('Moving!\n    (0,0) -> (%.3f,%.3f)'%(loc[0],loc[1])))

    # create a tool object (toolpath object)
    tool = Tool()
    # load the gcode into the tool object
    tool.build(gcode)
    # adjust the z position at each point by the given amount
    tool.zcorrect(correction_surface)

    ''' the follwing doe not work. is gcode.update(tool) broken?'''
    # load the changes back into the gcode object
    # append the modified g code to the empty list called out
    # out.append([gcode])
    # gcode.update(tool)
    # out = gcode
    # convert gcode to text format
    # output = ''.join([o.getGcode(tag=args.name) for o in out])
    # output = ''.join([out.getGcode()])

    '''instead the following simgle lin suffices'''
    '''is any info lost by doing it this way? E F M'''
    # generate a gcode file from the tool object
    output = tool.buildGcode()

    # get an output file name
    outfile = FILEENDING.join(os.path.splitext(gfile))
    print "outfile is:"
    print outfile
    # tell the user
    puts(colored.green('Writing: %s'%outfile))
    # write to file
    f = open(outfile,'w')
    f.write(output)
    '''
    with open(outfile,'w') as f:
        f.write(output)
    '''
    # how long did this take?
    puts(colored.green('Time to completion: %s'%(deltaTime(start))))
    print


if __name__ == '__main__':
    start = datetime.now()

    args = argv.arg(description='PyGRBL gcode imaging tool',
                    getFile=True, # get gcode to process
                    getMultiFiles=True, # accept any number of files; WHY MUST THIS BE TRUE for it to work?
                    otherOptions=EXTRAARGS, # "Install some nice things" very descriptive!!!
                    getDevice=False) # We dont need a device

    '''
    if type(args.z_surf) == str:
        print "using the z surface file"
        print args.z_surf
        surface_file_name = args.z_surf
    else:
        print "looking for a z correction surface file in the default name: probe_test.out"
        surface_file_name = 'probe_test.out'
    '''

    surface_file_name = args.z_surf
    #print "using the z surface file"
    #print args.z_surf


    # optimize each file in the list
    for gfile in args.gcode:
        # only process things not processed before.
        # c = re.match(r'(?P<drill>\.drill\.tap)|(?P<etch>\.etch\.tap)', gfile.name)
        #puts(colored.blue('Z correcting the G code file: %s'%(gfile.name)))
        c = re.match(r'(.+)(\.tap)', gfile.name)
        # c = True # HAX and accept everything
        if c: # either a drill.tap or etch.tap
            puts(colored.blue('Using the z surface file: %s'%(args.z_surf)))
            zcorrect_file(gfile.name, surface_file_name) #args=args)


    print '%s finished in %s'%(args.name,deltaTime(start))
