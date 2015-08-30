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


class CorrectionSurface():
    def __init__(self,surface_file_name = ''):
        self.x_step = "nan"
        self.y_step = "nan"
        self.array = []
        if surface_file_name != '':
            #print 'this is the surface correcion name that init is loading'
            #print surface_file_name
            self.Load_Correction_Surface(surface_file_name)
        else:
            self.Load_Correction_Surface()

    def Load_Correction_Surface(self, surface_file_name = 'probe_test.out' ):

        #initialize and load the correction surface
        Surface_Data = []
        Surface_Data = np.loadtxt(surface_file_name, delimiter=',', comments = '#')
        #correction_surface.array = Surface_Data
        self.array = Surface_Data

        #display the dataset to be used
        puts(colored.yellow('Surface Z Data Matrix'))
        puts(colored.yellow(np.array_str(Surface_Data)))
        #print Surface_Data

        probe_data_file = open(surface_file_name)

        #probe_data = probe_data_file.read()

        # retrieve the X and Y step sizes that scale the correction surface
        for line in probe_data_file:
            line = line.strip()

            if re.search('#', line,flags = re.IGNORECASE):
                #puts(colored.green('extracting scale data from file header'))
                #puts(colored.green( line))
                if re.search(' X_STEP:', line,flags = re.IGNORECASE):
                    #X_STEP:,0.5000
                    X_STEP_INFO = re.findall('X_STEP:,\d*\.\d*,', line, flags = re.IGNORECASE)[0]
                    if X_STEP_INFO:
                        X_STEP = float(X_STEP_INFO.split(',')[1])
                        puts(colored.yellow( 'x step size: {:.4f}'.format(X_STEP)))
                        #correction_surface.x_step = X_STEP
                        self.x_step = X_STEP
                else:
                    puts(colored.red( 'x step size: not found!'))
                if re.search(' Y_STEP:', line,flags = re.IGNORECASE):
                    #X_STEP:,0.5000
                    Y_STEP_INFO = re.findall('Y_STEP:,\d*\.\d*,', line, flags = re.IGNORECASE)[0]
                    if Y_STEP_INFO:
                        Y_STEP = float(Y_STEP_INFO.split(',')[1])
                        puts(colored.yellow( 'Y step size: {:.4f}'.format(Y_STEP)))
                        #correction_surface.Y_step = Y_STEP
                        self.y_step = Y_STEP
                else:
                    puts(colored.red( 'Y step size: not found!'))
        return self

    def estimate_surface_z_at_pozition(self,x,y):
        #find the bounding triangle on the correction surface closest to the x,y coordinet
        #begin with using the nearest node to the point
        Ns_x = round(x/self.x_step)
        Ns_y = round(y/self.y_step)
        # calcualte the boundaries
        Nmax_x = self.array.shape[0]
        Nmax_y = self.array.shape[1]
        #calculate distance from the nearest node
        epsilon_x= x - Ns_x*self.x_step
        epsilon_y= y - Ns_y*self.x_step
        #find the next two nearest nodes
        if (x > Ns_x*self.x_step):
            Nf_x = Ns_x + 1
            delta_x = self.x_step
        else:
            Nf_x = Ns_x + -1
            delta_x = -1.0*self.x_step
        if (y > Ns_y*self.x_step):
            Nf_y = Ns_y + 1
            delta_y = self.y_step
        else:
            Nf_y = Ns_y + -1
            delta_y = -1.0*self.y_step

        #force the data into the boundaries
        if Ns_x<0:
            Ns_x = 0
        if Ns_y<0:
            Ns_y = 0
        if Nf_x<0:
            Nf_x = 0
        if Nf_y<0:
            Nf_y = 0

        if Ns_x>Nmax_x:
            Ns_x = Nmax_x
        if Ns_y>Nmax_y:
            Ns_y = Nmax_y
        if Nf_x>Nmax_x:
            Nf_x = Nmax_x
        if Nf_y>Nmax_y:
            Nf_y = Nmax_y

        #calculate the slopes (x and y) of the plane defined by the triangle of bounding nodes
        slope_x = (self.array[Nf_x][Ns_y] - self.array[Ns_x][Ns_y])/delta_x
        slope_y = (self.array[Ns_x][Nf_y] - self.array[Ns_x][Ns_y])/delta_y
        #use the slope information and the origin intercept at the clsest node
        # to estimate the z position of the surface
        z_at_position = self.array[Ns_x][Ns_y] + epsilon_x*slope_x + epsilon_y*slope_y
        return z_at_position
