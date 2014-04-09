#!/usr/bin/env python
# orient.py -- determines the orientation of the edge location

# system
import sys

# installed
import cv
import cv2
import pylab
import numpy as np

# Package
from lib.communicate import Communicate





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






def findcircle():

    capture = cv.CaptureFromCAM(0)
    cv.WaitKey(200)

    # frame = cv.QueryFrame(capture)
    # gray = cv.CreateImage(cv.GetSize(frame), 8, 1)
    # edges = cv.CreateImage(cv.GetSize(frame), 8, 1)


    font = cv.InitFont(cv.CV_FONT_HERSHEY_DUPLEX, 1, 1, 0, 2, 8)
    ncirc = 0
    while True:
       frame = cv.QueryFrame(capture)
       im = np.array(cv.GetMat(frame))
       gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
       blur = cv2.medianBlur(gray, 5)
       blur = cv2.medianBlur(blur, 5)
       blur = cv2.medianBlur(blur, 5)
       # blur = cv2.blur(blur, 5)
       # im = blur
   
       circles = cv2.HoughCircles(blur, cv.CV_HOUGH_GRADIENT, 1,20,
                                param1=100,param2=30,minRadius=9,maxRadius=20)
   
       try:
           # circles = np.uint16(np.around(circles))
           n = np.shape(circles)
           if len(n) == 0:
               continue
           circles = np.reshape(circles,(n[1],n[2]))
           d = 999.0
           for x,y,r in circles:
               cv2.circle(im,(x,y),r,(0,0,255))
               cv2.circle(im,(x,y),2,(0,0,255),3)
               nd = (x-320)**2.0 + (y-240)**2.0
               if nd < d:
                   tmp = x,y,r
                   d = nd

           x,y,r = tmp
           cv2.circle(im,(x,y),r,(255,255,255))
           if ncirc == 0:
               circle = tmp
           else:
               circle = map(np.sum, zip(circle,tmp))
           ncirc += 1
           x,y,r = [int(c/float(ncirc)) for c in circle]
           cv2.circle(im,(x,y),r,(255,0,255))
           cv2.circle(im,(x,y),2,(255,0,255),3)
       
           if ncirc == 20: ncirc=0
       
      
       except Exception as e:
           raise
           print 'x',
   
       frame = cv.fromarray(im)
       cv.PutText(frame, "orient.py", (10,460), font, cv.RGB(17, 110, 255))
       cv.Line(frame, (320,0), (320,480) , 255)
       cv.Line(frame, (0,240), (640,240) , 255)
       cv.Circle(frame, (320,240), 100, 255)
   
       cv.ShowImage("Window",frame)
       c = (cv.WaitKey(16) & 255)
   
       if c in [27, 113]: #Break if user enters 'Esc', 'q'.
          break
       elif c != 255:
           print c


def findrowline(frame):
    hmin = 5 
    hmax = 6 # hmax = 180
    # saturation
    smin = 50
    smax = 100
    # value
    vmin = 250
    vmax = 256
    
    
    tmp = cv.CreateImage(cv.GetSize(frame), 8, 1)
    # tmp = cv.cvCloneImage(frame)
    cv2.cvCvtColor(frame, tmp, cv.CV_BGR2HSV) # convert to HSV
    # split the video frame into color channels
    cv.cvSplit(hsv_image, h_img, s_img, v_img, None)

    # Threshold ranges of HSV components.
    cv.cvInRangeS(h_img, hmin, hmax, h_img)
    cv.cvInRangeS(s_img, smin, smax, s_img)
    cv.cvInRangeS(v_img, vmin, vmax, v_img)
    cv.cvAnd(h_img, v_img, laser_img)
    
    
    return laser_img
    

def findrow2(frame):
    # return frame
    im = np.array(cv.GetMat(frame))
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    # thresh = cv2.adaptiveThreshold(gray, maxValue=255, 
    #                     adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                     thresholdType=cv2.THRESH_BINARY,
    #                     blockSize=3, C=127)
    
    contours,hier = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    
    # thresh = cv2.dilate(thresh, 3)
    kernel = np.ones((2,2),'uint8')
    thresh = cv2.dilate(thresh, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    delta = 20
    for i in np.arange(0,thresh.shape[0],delta):
        ii = np.argmax(np.mean(thresh[i:i+delta,20:thresh.shape[1]-20], axis=0))
        thresh[i:i+delta,:] = 0
        thresh[i:i+delta,ii] = 255
        # return cv.fromarray(thresh)
    
    return cv.fromarray(thresh)
    
    try:
        cnt = contours[0]
    
        # then apply fitline() function
        [vx,vy,x,y] = cv2.fitLine(cnt,cv2.cv.CV_DIST_L2,0,0.01,0.01)

        # Now find two extreme points on the line to draw line
        lefty = int((-x*vy/vx) + y)
        righty = int(((gray.shape[1]-x)*vy/vx)+y)
    
        cv2.line(im,(gray.shape[1]-1,righty),(0,lefty),255,2)
    
        return cv.fromarray(im)
    except:
        return frame





class Camera(object):
    def __init__(self, cameranumber=0):
        self.status = ''
        self.cam = cv.CaptureFromCAM(cameranumber)
        self.update() # setup frame
        
        self.size = cv.GetSize(self.frame)
        self.center = tuple(x/2 for x in self.size)
        
        self.font = cv.InitFont(cv2.FONT_HERSHEY_DUPLEX, 0.5, 0.8, 
                                shear=0, thickness=1, lineType=8)
        self.font2 = cv.InitFont(cv2.FONT_HERSHEY_DUPLEX, 0.5, 0.8, 
                                shear=0, thickness=3, lineType=8)
        
        self.color = cv.RGB(100, 130, 255)
    
    def write(self, msg, loc):
        cv.PutText(self.frame, msg, loc, self.font2, 0)
        cv.PutText(self.frame, msg, loc, self.font, self.color)
    
    def update(self, frame=None):
        if frame:
            self.frame = frame
        else:
            self.frame = cv.QueryFrame(self.cam)
    
    def addoverlay(self):
        # cv.PutText(self.frame, "orient.py", (10,self.size[1]-10), self.font, self.color)
        self.write('orient.py', (10,self.size[1]-10) )
        cv.Line(self.frame, (0,self.center[1]), (self.size[0],self.center[1]), self.color)
        cv.Line(self.frame, (self.center[0],0), (self.center[0],self.size[1]), self.color)
        cv.Circle(self.frame, self.center, 100, self.color)
        
        value = 0
        count = 100
        def onChange(x,*args):
            print x
        cv.CreateTrackbar('test','Window', value, count, onChange)
    
    def display(self, text):
        # cv.PutText(self.frame, text, (20,20), self.font, self.color)
        self.write(text, (20,20))
    
    def show(self):
        cv.ShowImage("Window", self.frame)
    
    def interact(self):
        c = (cv.WaitKey(25) & 0xFF)
        
        CHARMAP = {
            27:'quit',     # q
            113:'quit',    # esc
            0:'forward',   # arrows
            1:'backward',
            2:'left',
            3:'right',
            97:'up',       # a
            122:'down',    # d
            43:'embiggen', # +
            95:'lessen',   # -
        }
        if c in CHARMAP:
            self.status = CHARMAP[c]
        elif c != 255:
            print repr(c)

class Controller(object):
    
    def __init__(self, serial):
        self.serial = serial
        self.serial.run('G20G91 (inch, incremental)')
        self.movelen = 0.1 #inch
    
    def run(self, cmd):
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
        else:
            return cmd
        
    def position(self):
        '''TODO convert this to some nice text'''
        status = self.serial.run('?')
        return 'position: {}'.format(status)





def main():
    
    with Communicate('', None, debug=True) as serial:
        camera = Camera()
        controller = Controller(serial)
        
        while True:
            camera.update()
            camera.interact()
            
            camera.status = controller.run(camera.status)
            if camera.status == 'quit':
                break
            else:
                camera.display(camera.status)
            
            camera.addoverlay()
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
    nsigma=1.0
    
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
            pylab.plot(imgavg)
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
    pylab.imshow(img, origin='lower', interpolation='nearest',
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
    
def capture():
    ''' This is a simple capture script. Type c to capture a frame 
    to the current directory named test.jpg.  Quit with q or esc.   
    This forces a high resolution image (1280 x 720). You can recapture 
    and overwrite the image with hitting c again.
    '''
    cap = cv.CaptureFromCAM(0)
    cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
    cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
    while True:
        img = cv.QueryFrame(cap)
        cv.ShowImage('window', img)
        c = (cv2.waitKey(16) & 0xFF)
        if c in [ord('q'),27]:
            break
        elif c == ord('c'):
            cv.SaveImage('test.jpg', img)


if __name__ == "__main__":
    if 'capture' in sys.argv:
        capture(sys.argv)
    elif 'test' in sys.argv:
        test()
    else:
        main()
