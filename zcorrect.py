#!/usr/bin/env python

#this code should use a 2 dimensional array of z_positions
#the element 0,0 is 0 and all other elements are relative z positions
#there should also be a probe_step_x value and a probe_step_y value
#these define the distsnces between the points measured in the z_positions array


#imports
from numpy import arange
from lib import argv
from lib.gparse import gparse
from lib.grbl_status import GRBL_status
from lib.communicate import Communicate
from clint.textui import puts, colored
import time, readline
import numpy as np
import re



def Load_Correction_Surface(surface_file_name = 'probe_test.out' ):

    #initialize and load the correction surface
    Surface_Data = []
    Surface_Data = np.loadtxt(surface_file_name, delimiter=',', comments = '#')
    correction_surface.array = Surface_Data
    #display the dataset to be used
    puts(colored.yellow('Surface Z Data Matrix'))
    print Surface_Data

    probe_data_file = open(surface_file_name)

    #probe_data = probe_data_file.read()

    # retrieve the X and Y step sizes that scale the correction surface
    for line in probe_data_file:
        line = line.strip()

        if re.search('#', line,flags = re.IGNORECASE):
            puts(colored.green('extracting scale data from file header'))
            puts(colored.green( line))
            if re.search(' X_STEP:', line,flags = re.IGNORECASE):
                #X_STEP:,0.5000
                X_STEP_INFO = re.findall('X_STEP:,\d*\.\d*,', line, flags = re.IGNORECASE)[0]
                if X_STEP_INFO:
                    X_STEP = float(X_STEP_INFO.split(',')[1])
                    puts(colored.yellow( 'x step size: {:.4f}'.format(X_STEP)))
                    correction_surface.x_step = X_STEP
            else:
                puts(colored.red( 'x step size: not found!'))
            if re.search(' Y_STEP:', line,flags = re.IGNORECASE):
                #X_STEP:,0.5000
                Y_STEP_INFO = re.findall('Y_STEP:,\d*\.\d*,', line, flags = re.IGNORECASE)[0]
                if Y_STEP_INFO:
                    Y_STEP = float(Y_STEP_INFO.split(',')[1])
                    puts(colored.yellow( 'Y step size: {:.4f}'.format(Y_STEP)))
                    correction_surface.Y_step = Y_STEP
            else:
                puts(colored.red( 'Y step size: not found!'))
    return correction_surface
