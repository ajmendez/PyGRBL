#!/usr/bin/env python
# orient.py -- determines the orientation of the edge location

# system
import sys
from collections import deque

# installed
import cv
import cv2
import pylab
import numpy as np

# Package
from lib.communicate import Communicate

__DOC__='''
arrows: move
a/d: up/down
c: find circle
+/-: step size
1-4: select hole
s: set location
'''






NOTE = '''
This is just a collection of links that I thought were interesting at the time.

http://uvhar.googlecode.com/hg/test/laser_tracker.py


http://stackoverflow.com/questions/14184147/detect-lines-opencv-in-object
https://github.com/bradmontgomery/python-laser-tracker
https://sites.google.com/site/todddanko/home/webcam_laser_ranger

http://shaneormonde.wordpress.com/2014/01/25/webcam-laser-rangefinder/
http://shaneormonde.wordpress.com/2014/01/30/2d-mapping-using-a-webcam-and-a-laser/


http://www.shapeoko.com/forum/viewtopic.php?f=28&t=1097
https://github.com/duembeg/gsat
http://www.shapeoko.com/forum/viewtopic.php?f=28&t=1097&start=10
http://blog.alessiovaleri.it/using-transform-matrix-for-pcb-drilling-part-1/
http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Axis_Embed_Video

http://zapmaker.org/projects/grbl-controller-3-0/


https://code.google.com/p/grecode/
https://github.com/bkubicek/grecode
http://www.turtlesarehere.com/html/pcb_drill.html
http://www.imajeenyus.com/electronics/20100709_excellon_g-code_converter/index.shtml

http://www.c21systems.com/CNCCam/

http://shakers.pixel-shaker.fr/?cat=154
http://comments.gmane.org/gmane.linux.distributions.emc.user/37790
http://techvalleyprojects.blogspot.com/2013/06/opencv-canny-edge-finding-contours-and.html
https://github.com/roblourens/facealign


http://stackoverflow.com/questions/5368449/python-and-opencv-how-do-i-detect-all-filledcircles-round-objects-in-an-image
http://stackoverflow.com/questions/11522755/opencv-via-python-on-linux-set-frame-width-height
'''




class Camera(object):
    def __init__(self, cameranumber=0):
        '''wrapper for a cv capture object.  Defaults to the 
        most recent camera (0).'''
        self.status = '' # current task at hand
        
        self.cam = cv.CaptureFromCAM(cameranumber)
        self.update() # setup self.frame
        
        self.shape = cv.GetSize(self.frame)
        self.center = tuple(x/2 for x in self.shape)
        self.currentcircles = deque(maxlen=40)
        self.points = deque(maxlen=100)

    def getfont(self, **kwargs):
        '''get a font with some nice defaults'''
        fontsize = kwargs.pop('fontsize', 0.5)
        outline = kwargs.pop('outline', False)
        params = dict(font=CV_FONT_HERSHEY_PLAIN,
                      hscale=fontsize*0.9, vscale=fontsize,
                      shear=0, thickness=1, 
                      lineType=cv2.CV_AA)
        params.update(kwargs)
        if outline:
            params['thickess'] += 2
        return cv.InitFont(**params)
    
    def getcolor(self, red=0, green=0, blue=0):
        '''wrapper around cv.RGB'''
        return cv.RGB(red,green,blue)
        
    def getdefaultcolor(self):
        '''A nice steel blue'''
        return self.getcolor(100,130,255)
    
    def write(self, msg, loc, lineheight=20, color=None, outline=True):
        '''Write a string(msg) to the screen. This handles new lines like 
        butter, and defaults to outlineing the text'''
        for i,line in enumerate(msg.splitlines()):
            l = (loc[0], loc[1]+i*lineheight)
            if outline:
                cv.PutText(self.frame, line, l, self.getfont(outline), 0)
            cv.PutText(self.frame, line, l, self.getfont(outline), self.color)
    
    def displaystatus(self, text):
        '''A wrapper that handles displaying of the current status'''
        self.write(text, (20,20))
    
    def update(self, frame=None):
        '''Update the current frame in the buffer. If you pass in a frame object
        it will use it.'''
        if frame:
            self.frame = frame
        else:
            self.frame = cv.QueryFrame(self.cam)
    
    def addoverlay(self):
        self.write(__DOC__, (10,20))
        self.write('orient.py', (10,self.size[1]-10) )
        cv.Line(self.frame, (0,self.center[1]), (self.size[0],self.center[1]), self.color)
        cv.Line(self.frame, (self.center[0],0), (self.center[0],self.size[1]), self.color)
        cv.Circle(self.frame, self.center, 100, self.color)
    
    def addtrackbar(self):
        '''Add a trackbar?!'''
        # value = 0
        # count = 100
        # def onChange(x,*args):
        #     print x
        # cv.CreateTrackbar('test','Window', value, count, onChange)
    
    
    def show(self):
        '''Display the current frame'''
        cv.ShowImage("Window", self.frame)
    
    def interact(self):
        '''Handle all of the fancy key presses'''
        c = (cv.WaitKey(25) & 0xFF)
        
        CHARMAP = {
            27:'quit',        # q
            113:'quit',       # esc
            0:'forward',      # arrows
            1:'backward',     #
            2:'left',         #
            3:'right',        #
            97:'up',          # a
            122:'down',       # d
            43:'embiggen',    # +
            95:'lessen',      # -
            # location setting
            115:'set',        # s
            49: 'lowerleft',  # 1
            50: 'upperleft',  # 2
            51: 'lowerright', # 3
            52: 'upperright', # 4
            # circle finding
            99: 'circle',     # c
        }
        if c in CHARMAP:
            self.status = CHARMAP[c]
        elif c != 255:
            print 'Key not recognized: {} [{}]'.format(repr(c), ord(c))
    
    # Line measuring functions
    
    def setupmeasure(self, color='red'):
        '''Setup the line measureing state.
        self.index -- which color should we focus on.
        self.nsigma -- how many sigma above background to fit
        self.zero  -- The vertical zero position of the laser line.'''
        self.index = ['blue','green','red'].index(color)
        self.nsigma = 1.0
        self.zero = 0
    
    def setzero(self, **kwargs):
        '''Set the zero location of the line location.'''
        self.zero = self.measure(**kwargs)
    
    def measure(self, delta=50, invert=False, getall=True, quiet=False):
        '''return the location of the point in pixels'''
        # DEBUG!! invert image so that a dark green line looks like a 
        #         bright red line!
        if invert:
            cv.Not(self.frame, self.frame)
        
        img = np.array(cv.GetMat(self.frame))[:,:,self.index]
        out = [] # store the found locations of the line location
        for i,im in vslice(img, delta):
            imavg = np.mean(im, axis=1)
            ex,ey,cut = findextreme(imavg, self.nsigma)
            try:
                p,x,g = fitgaussian(ex,ey,cut)
                out.append([i,p['mean'].value])
            except KeyboardInterrupt as e:
                print 'User canceled operation'
                return -1.0
            except Exception as e:
                if not quiet:
                    print 'Failed to fit: {} {}'.format(i,e)
                # raise
        try:
            x,y = zip(*out)
        except:
            x,y = [0],[0]
        if getall:
            return x,y
        else:
            return np.mean(y)
    
    def plot(self, xx, yy, pos=None, size=None):
        
        # show the mean
        x = np.mean(xx)
        y = np.mean(yy)
        cv.Circle(self.frame, (int(x),int(y)), 5, self.getdefaultcolor())
        
        # rolling plot of the mean
        # self.points.append(int(yy))
        # for x,y in enumerate(self.points):
        #     cv.Circle(self.frame, (x,y), 2, self.getcolor(red=1))
        
        # show all points
        for x,y in zip(xx,yy):
            cv.Circle(self.frame, (int(x),int(y)), 2, self.getdefaultcolor())
        
        # show all the rolling points
        self.points.append([xx,yy])
        for i,(xx,yy) in enumerate(self.points):
            for x,y in zip(xx,yy):
                cv.Circle(self.frame, (int(i+x-len(self.points)/2.0),int(y)), 1, self.getcolor(red=0.5))
        
        
        
        # if pos is None: pos = 0,0
        # if size is None: size = 50,200
        # self.points.append(z)
        # for x in self.points:
        #     try:
        #         cv.Circle(self.frame, (0, int(x)), 10, self.getdefaultcolor())
        #     except:
        #         print x
        
    
    
    # Circle finding procedures
    
    def circle(self):
        '''Determine the location of a circle in the frame.'''
        frame = np.array(cv.GetMat(self.frame))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # img = cv2.medianBlur(img, 5)
        circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 
                                   dp=1,  # accumulator res
                                   minDist=40, #min dist to next circle
                                   param1=150, # canny param
                                   param2=15, # accumulator threshold
                                   minRadius=7,
                                   maxRadius=25)
        
        try:
            n = np.shape(circles)
            if len(n) == 0:
                raise ValueError('No Circles!')
            circles = np.reshape(circles,(n[1],n[2]))
            for x,y,r in circles:
                cv2.circle(frame,(x,y),r,(255,255,255))
                cv2.circle(frame,(x,y),2,(255,255,255),2)
            
            # add the most central one is the good one
            tmp = self.centralitem(circles)
            if tmp is not None:
                cv2.circle(frame,(tmp[0],tmp[1]),tmp[2],(0,255,0),2)
                self.currentcircles.append(tmp)
        except Exception as e:
            print e
        
        frame = self.plotcurrentcircle(frame)
        self.frame = cv.fromarray(frame)
    
    def plotcurrentcircle(self, frame):
        '''Plot the most central circle -- this can fail due to
        not having any points so wrap it and ignore its failings as 
        a program.  It is ok program I still enjoy your work.'''
        try:
            # plot the average one
            x,y,r = map(np.mean, zip(*self.currentcircles))
            cv2.putText(frame, '{:0.1f}, {:0.1f}, {:0.2f}'.format(x,y,r),
                        (int(x+20),int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0,0,255), 1)
            cv2.circle(frame,(x,y),r,(0,0,255),2)
            cv2.circle(frame,(x,y),2,(0,0,255),2)
        except:
            pass
        return frame

    def centralitem(self, items):
        '''Get the most central item from a list of (x,y,...) items'''
        mindist = 1e4
        good = None
        for item in items:
            dist = (item[0]-self.center[0])**2.0 + (item[1]-self.center[1])**2.0
            if dist <= mindist:
                good = item
                mindist = dist
        return good






class Controller(object):
    def __init__(self, serial):
        '''Controller for the serial -> grbl device. Generally this assumes
        that the machine is in incremental mode.'''
        self.serial = serial
        self.serial.run('G20G91 (inch, incremental)')
        self.movelen = 0.1 #inch
    
    def run(self, cmd):
        '''Run a gcode-command, or a specific keyword.  (e.g. forward will move
        the machine forward in the x direction by self.movelen.)  This also 
        handles increasing and decreasing the self.movelength command. 
        If this does not consume the command it is returned. Or it 
        returns a nice status message of what happened.'''
        DELTA = 0.001
        CMD = dict(
            forward='X',
            backward='X-',
            left='Y',
            right='Y-',
            up='Z',
            down='Z-',
            embiggen=DELTA,
            lessen=-DELTA,
        )
        
        if cmd in CMD:
            d = CMD[cmd]
            if isinstance(d, str):
                self.serial.run('G0 {dir}{move:0.3f}'.format(dir=d, move=self.movelen))
                return self.position()
            elif cmd in ['embiggen', 'lessen']:
                self.movelen += d
                if self.movelen > 1: 
                    self.movelen = 1.0
                elif self.movelen <= 0:
                    self.movelen = DELTA
                return 'movelen: {:0.3f}inch'.format(self.movelen)
        elif 'G' in CMD:
            self.serial.run(cmd)
            return 'Ran: {}'.format(cmd)
        else:
            return cmd
    
    def setposition(self, cmd):
        '''This consumes the commands that are related to figuring out
        the location of a set of locations (corners of a board).'''
        POS = ['set', 'lowerleft','lowerright','upperleft','upperright']
        if cmd in pos:
            return 'Set: {}'.format(cmd)
        else:
            return cmd
    
    def position(self):
        ''' get the current state of the machine and then return a processed
        bit of text for simple consuming by other programs.
        TODO: debug what the machine actually produces.
        '''
        status = self.serial.run('?')
        return 'position: {}'.format(status)
    
    
    # x+y scan related procedures
    
    def setupscan(self):
        '''Get the variables from the command line.
        e.g. p orient.py scan [width] [height] [number of pts]'''
        self.x = 0
        self.y = 0
        try:
            self.width = int(sys.argv[2])
            self.height = int(sys.argv[3])
            self.npts = int(sys.argv[4])
        except Exception as e:
            print e
            raise ValueError('Could not parse the arguments'+
                             'pass in {} scan [width] [height] [pts] :: [{}]'
                             .format(sys.argv[0], sys.argv[2:]))

    def scan(self):
        '''scan over the width and heigh with npts locations.'''
        for x in np.linspace(0,self.width, self.npts):
            for y in np.linspace(0, self.height, self.npts):
                self.run('G0 X{:0.3f} Y{:0.2f}'.format(x,y))
                yield x,y






def findcircles():
    '''Find the current circle closest to the center of the screen.
    this will show all circles on the screen.'''
    with Communicate('', None, debug=True) as serial:
        camera = Camera()
        controller = Controller(serial)
        
        while True:
            camera.update()
            camera.interact()
            
            # camera.status = controller.run(camera.status)
            # camera.status = controller.position(camera.status)
            if camera.status == 'quit':
                break
            else:
                camera.display(camera.status)
                camera.status = 'circle'
                camera.circle()
            #     
            # 
            camera.addoverlay()
            camera.show()






def scan():
    pylab.ion()
    pylab.figure(1)
    
    
    with Communicate('', None, debug=True) as serial:
        serial.timeout = 0.0001
        camera = Camera()
        camera.setupmeasure()
        
        controller = Controller(serial)
        controller.setupscan()
        
        out = []
        for x,y in controller.scan():
            camera.update()
            camera.interact()
            
            z = camera.measure()
            out.append([x,y,z])
            
            if camera.status == 'quit':
                break
            camera.show()
            
            if len(out) > 0:
                pylab.cla()
                tmp = zip(*out)
                sc = pylab.scatter(tmp[0],tmp[1],s=tmp[2], c=tmp[2], vmin=0, vmax=400)
                print '{: 8.3f} {: 8.3f} {: 8.3f}'.format(x,y,z)
            
        pylab.ioff()
        pylab.show()
            


def roll():
    camera = Camera()
    camera.setupmeasure()
    while True:
        camera.update()
        camera.interact()
        x,y = camera.measure(getall=True, quiet=True)
        camera.plot(x,y)
        if camera.status == 'quit':
            break
        camera.show()
        



from pysurvey.plot import line, setup, legend, minmax, embiggen
from lmfit import minimize, Parameters, report_errors, conf_interval, report_ci

def vslice(img, delta=20):
    '''Generates delta slices of an image that can be used
    to find points as a function of the x axis.  returns the 
    middle pixel location and the image that is [heightxdelta] in
    size.'''
    for i,index in enumerate(np.arange(0,img.shape[1],delta)):
        middle = int(np.mean([index,index+delta]))
        yield middle, img[:,index:index+delta]

def findextreme(x, nabove=1.0):
    '''Returns the index, array values, and cut value of the array
    that is above the median and nabove*sigma of the array. This attempts
    to find any line that is above the background.'''
    cut = np.median(x) + nabove*np.std(x)
    ii = np.where(x >= cut)[0]
    return ii, x[ii], cut

def getimrange(x, imrange):
    xmin,xmax = minmax(x)
    if imrange[0] > xmin:
        imrange[0] = xmin
    if imrange[1] < xmax:
        imrange[1] = xmax
    return imrange


def gauss2(p, x, y=None):
    '''A simple gaussian fit function.  p is a Parameters() object
    that has an amplitude, mean, and sigma value.  Without setting
    y this returns the gaussian.  with y it returns the deviation from
    the fit gaussian -- used for fitting.'''
    if y is None:
        y = np.zeros(len(x))
    return (p['amplitude'].value*
            np.exp(-(x-p['mean'].value)**2/(2.*p['sigma'].value**2))
            # + p['offset'].value
            - y
            )

def getarray(width=1000, delta=0.1):
    '''Get an array to plot the gaussian.
    There should be a better way of doing this.'''
    return np.arange(0, width, delta)

def fitgaussian(x,y,offset=0):
    '''Fit a gaussian to the data points x,y.  
    offset == the assumed floor for the gaussian (subtracted from 
    the y array).  Originally I fit for both the amplitude and offset
    however this sometimes caused issues due to the degeneracy. '''
    
    # set the parameters and some min values
    p = Parameters()
    # generally the background is 20-30, so require at least 10 above that
    p.add('amplitude', value=np.max(y)-offset, min=10)
    p.add('mean', value=np.mean(x), min=0)
    p.add('sigma', value=np.std(x), min=0)
    
    
    # minimise the fit.
    out = minimize(gauss2, p, args=(x, y-offset) )
    # print the fit values and uncert.  I may want to check the 
    # out.success value to ensure that everything worked.
    # report_errors(p)
    
    r = embiggen(minmax(x),0.2)
    xx = np.arange(r[0], r[1], 0.1)
    return p, xx, gauss2(p,xx)+offset


def test(color='green', delta=20):
    '''This is a simple testing function that loads an image and 
    attemps to find a line in it. Originally I attempted to use fit
    a quadratic to the extreme bit of the data.  This was ok, but did 
    not capture the pointy-ness of the line.  Now I am using a guass fit.
    '''
    directory = '/Users/ajmendez/Dropbox/Shared/Design/laser/test/'
    # Image from the web.
    filename = directory+'1mW-635nm-Red-Laser-Module-Focused-Line-M635AL12416120_1.jpg'
    color='red'
    nsigma=1.0
    # filename = directory + 'test2.jpg' # has ripples
    # filename = directory + 'test.jpg'
    filename = directory + 'debug_green.jpg'
    color='green'
    nsigma=1.5
    
    filename = directory+'/test_circ.jpg'
    color='green'
    nsigma=0.0
    
    out = []
    img = cv2.imread(filename)
    imrange = [img.shape[1],0]
    index = ['blue','green','red'].index(color)
    setup(figsize=(8,8), subplt=(2,2,2))
    cmap  = pylab.cm.winter
    cmap2 = pylab.cm.Blues
    cmap3 = pylab.cm.Reds
    
    for i,im in vslice(img, delta):
        imavg = np.mean(im[:,:,index], axis=1)

        ex,ey,cut = findextreme(imavg, nsigma)
        imrange = getimrange(ex,imrange)
        try:
            p,x,g = fitgaussian(ex,ey,cut)
            mid = p['mean'].value
            
            # plot the fit
            ic = 200*i/img.shape[1]+55
            # line(x=mid, alpha=0.5, color=cmap(ic))
            pylab.plot(ex,ey, alpha=0.7, color=cmap2(ic))
            pylab.plot(x,g, alpha=0.7, color=cmap3(ic))
            
            # Draw it to the image and then save the value
            # cv2.circle(img, (i,int(mid)), 2, 255)
            out.append([i,mid])
            print i, mid
        except Exception as e:
            pylab.plot(ex, ey)
            pylab.show()
            raise
            print e
            # cv2.circle(img, (i,0), 10, (0,0,255))
    # Ensure that there is some space around the image
    setup(xr=imrange, embiggenx=0.2, embiggeny=0.2)
    
    x,y = map(np.array, zip(*out))
    p = np.polyfit(x,y,1)
    fit = p[0]*x + p[1]
    diff = y - fit
    ns = np.std(diff)
    
    # next subplts -- add some extra analysis
    setup(subplt=(2,2,1), title='Points offset by 100px',
          xr=[0,img.shape[1]], yr=[0,img.shape[0]])
    pylab.imshow(img[:,:,[2,1,0]], origin='lower', interpolation='nearest',
                 aspect='equal')
    # pylab.plot(x,y+100, '.', color='white', markeredgewidth=1)
    pylab.scatter(x, y+100, marker='.', vmin=0, vmax=255, linewidth=0.4,
                  c=200*x/img.shape[1]+55, edgecolor=(1,1,1,0.5), cmap=cmap2)
    
    # deviation from a line
    setup(subplt=(4,2,5), ylabel='line and fit', xticks=False)
    pylab.plot(x, y, color='blue', linewidth=2, alpha=0.7)
    pylab.plot(x, fit, color='red', linewidth=2, alpha=0.7)
    
    setup(subplt=(4,2,7), ylabel='Deviation from \nline [pixel]')
    pylab.plot(x, diff)
    
    setup(subplt=(2,2,4), 
          title='Sigma:{:0.2f}px'.format(ns),
          xlabel='Deviation distribution [pixel]')
    pylab.hist(diff, np.arange(-3*ns,3*ns,ns/2.0))
    line(x=[np.mean(diff),
            np.mean(diff)-np.std(diff), 
            np.mean(diff)+np.std(diff)])
    pylab.tight_layout()
    pylab.show()




def test_circle():
    directory = '/Users/ajmendez/Dropbox/Shared/Design/laser/test/'
    filename = directory+'/test_circ.jpg'
    frame = cv2.imread(filename)
    
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # img = cv2.GaussianBlur(img, (0,0), 2.1)
    
    
    tmp = cv2.GaussianBlur(img, (0,0), 5.1)
    img = cv2.addWeighted(img,3.0,tmp, -2.0, -0.1)
    
    # cv2.threshold(img, 120, 0, cv2.THRESH_TOZERO, img)l
    
    # img = cv2.GaussianBlur(img, (0,0), 2.1)
    # cv2.adaptiveThreshold(img, 256, cv2.ADAPTIVE_THRESH_MEAN_C,
    #                       cv2.THRESH_BINARY_INV, 5, 0, img)
    # img = cv2.GaussianBlur(img, (0,0), 2.1)
    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, (3,3))
    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, (5,5))
    # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, (3,3))
    # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, (5,5))
    # img = cv2.GaussianBlur(img, (0,0), 5.1)
    
    # cv2.imshow('window',img)
    # cv2.waitKey()
    
    # img = cv2.medianBlur(img, 5)
    # img = cv2.medianBlur(img, 3)
    # img = cv2.GaussianBlur(img, (0,0), 0.1)
    frame = img
    
    circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 
                               dp=1,  # accumulator res
                               minDist=40, #min dist to next circle
                               param1=100, # canny param
                               param2=20, # accumulator threshold
                               minRadius=10,
                               maxRadius=20)
    try:
        n = np.shape(circles)
        if len(n) == 0:
            raise ValueError('No Circles!')
        circles = np.reshape(circles,(n[1],n[2]))
        for x,y,r in circles:
            cv2.putText(frame, '{:0.2f}'.format(r),
                        (int(x+2),int(y+2)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0,0,255), 2)
            
            cv2.circle(frame,(x,y),r,(0,0,255))
            cv2.circle(frame,(x,y),2,(0,0,255),3)
        # cv2.circle(img,(x,y),r,(255,255,255))
        # self.frame = cv.fromarray(img)
    except Exception as e:
        print 'Failed: {}'.format(e)
    
    cv2.imshow('window',frame)
    cv2.waitKey()
    



def capture():
    ''' This is a simple capture script. Type c to capture a frame 
    to the current directory named test.jpg.  Quit with q or esc.   
    This forces a high resolution image (1280 x 720). You can recapture 
    and overwrite the image with hitting c again.
    '''
    cap = cv.CaptureFromCAM(0)
    # cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    # cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
    while True:
        img = cv.QueryFrame(cap)
        
        cv.ShowImage('window', img)
        c = (cv2.waitKey(16) & 0xFF)
        if c in [ord('q'),27]:
            break
        elif c == ord('c'):
            print 'Saved Frame!'
            cv.SaveImage('test.jpg', img)


if __name__ == "__main__":
    if 'capture' in sys.argv:
        capture()
    elif 'test' in sys.argv:
        test()
    elif 'circle' in sys.argv:
        test_circle()
    elif 'scan' in sys.argv:
        scan()
    elif 'roll' in sys.argv:
        roll()
    else:
        main()
