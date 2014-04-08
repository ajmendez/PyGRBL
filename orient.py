#!/usr/bin/env python
# orient.py -- determines the orientation of the edge location
import numpy as np
import pylab
import cv
import cv2
from lib.communicate import Communicate
















'''
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
   
       # 
       # 
       # # cv.CvtColor(frame, gray, cv.CV_BGR2GRAY)
       # gray = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2GRAY)
       # blur = cv2.GaussianBlur(gray, (3,3), 0)
       # 
       # # GaussianBlur( src_gray, src_gray, Size(9, 9), 2, 2 );
       # 
       # # storage = cv.CreateMat(frame.width, 1, cv.CV_32FC3)
       # # cv.HoughCircles(edges, storage, cv.CV_HOUGH_GRADIENT, 25, 100, 200, 10)
       # circles = cv2.HoughCircles(gray, cv.CV_HOUGH_GRADIENT, 3, 100, None, 200, 100, 5, 16)
       # 
       # n = np.shape(circles)
       # circles = np.reshape(circles,(n[1],n[2]))
       # # print circles
       # for circle in circles:
       #     cv2.circle(frame,(circle[0],circle[1]),circle[2],(0,0,255))
       # 
       # # for i in xrange(storage.width - 1):
       # #     radius = storage[i, 2]
       # #     center = (storage[i, 0], storage[i, 1])
       # #     cv.Circle(frame, center, radius, (0, 0, 255), 3, 8, 0)
       # 
       # 
       # cv.PutText(frame, "orient.py", (10,460), font, cv.RGB(17, 110, 255))
       # cv.Line(frame, (320,0), (320,480) , 255)
       # cv.Line(frame, (0,240), (640,240) , 255)
       # cv.Circle(frame, (320,240), 100, 255)
       # 
       # cv.ShowImage("Window",frame)
       # c = (cv.WaitKey(16) & 255)
       # 
       # if c in [27, 113]: #Break if user enters 'Esc', 'q'.
       #    break
       # elif c != 255:
       #     print c

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
    



from pysurvey.plot import line, setup, legend, minmax
from scipy.optimize import curve_fit

def vslice(img, delta=20):
    for i,index in enumerate(np.arange(0,img.shape[1],delta)):
        middle = int(np.mean([index,index+delta]))
        yield middle, img[:,index:index+delta]

def findextreme(x, nabove=1.0):
    cut = np.median(x) + nabove*np.std(x)
    ii = np.where(x >= cut)[0]
    return ii, x[ii], cut

def fitquad(x,y):
    xx = np.arange(0,1000,0.1)
    a,b,c = np.polyfit(x,y,2)
    yy = c + b*xx + a*xx**2.0
    jj = np.where(yy > 0)[0]
    return xx[jj],yy[jj]

def gauss(x, *p):
    c, A, mu, sigma = p
    return c+A*np.exp(-(x-mu)**2/(2.*sigma**2))

def fitgauss(x,y,offset=0):
    xx = np.arange(0, 1000, 0.1)
    p0 = [offset, np.max(y)-offset, np.mean(x), np.std(x)]
    coeff, var_matrix = curve_fit(gauss, x, y, p0=p0)
    gg = gauss(xx, *coeff)
    return xx,gg


from lmfit import minimize, Parameters, report_errors, conf_interval, report_ci
def gauss2(p, x, y=None):
    if y is None:
        y = np.zeros(len(x))
    return (p['amplitude'].value*
            np.exp(-(x-p['mean'].value)**2/(2.*p['sigma'].value**2))
            # + p['offset'].value
            - y
            )

def fitgauss2(x,y,offset=0):
    p = Parameters()
    # p.add('offset', value=offset, min=50)
    p.add('amplitude', value=np.max(y)-offset, min=10)
    p.add('mean', value=np.mean(x), min=0)
    p.add('sigma', value=np.std(x), min=0)
    
    out = minimize(gauss2, p, args=(x, y-offset) )
    
    # report_errors(p)
    
    xx = np.arange(0,1000,0.1)
    return xx, gauss2(p,xx)+offset
    
    

def test():
    # filename = '/Users/ajmendez/Dropbox/Shared/Design/laser/test/1mW-635nm-Red-Laser-Module-Focused-Line-M635AL12416120_1.jpg'
    filename = '/Users/ajmendez/Dropbox/Shared/Design/laser/test/debug_green.jpg'
    img = cv2.imread(filename)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    out = []
    for i,im in vslice(img):
        vv = np.mean(im[:,:,1], axis=1)
        
        ii,v,cut = findextreme(vv, 0.2)
        # x,y = fitquad(ii,v)
        
        
        try:
            # xx,gg = fitgauss(ii,v,cut)
            xx,gg = fitgauss2(ii,v,cut)
            
            # setup(xr=[260,300])
            # pylab.plot(vv)
            # pylab.plot(xx,gg)
            
            mid = xx[np.argmax(gg)]
            print i, mid
            cv2.circle(img, (i,int(mid)), 2, 255)
            out.append([i,mid])
        except Exception as e:
            print e
            # zz,gz = fitgauss2(ii,v,cut)
            
            # setup(xr=minmax(ii))
            # pylab.plot(ii,v)
            # pylab.plot(xx,gg)
            # pylab.plot(zz,gz)
            # line(y=cut)
            # pylab.show()
            # return
            cv2.circle(img, (i,0), 10, 75)
        
        # setup(figsize=(14,6), subplt=(1,3,1))
        # pylab.imshow(im, interpolation=None, origin='lower', aspect='auto')
        # 
        # setup(subplt=(1,3,2))
        # pylab.plot(vv)
        # pylab.plot(ii, v)
        # line(y=cut)
        # 
        # 
        # setup(subplt=(1,2,2), xr=minmax(ii))
        # pylab.plot(vv, '-s')
        # pylab.plot(x,y)
        # pylab.plot(xx,gg)
        # 
        # 
        # setup(embiggenx=0.2, embiggeny=0.2)
        # line(y=cut, x=x[np.argmax(y)], color='r')
        # line(y=cut, x=np.average(ii,weights=v), color='k')
        # line(y=cut, x=xx[np.argmax(gg)], color='b')
        # 
        # 
        # pylab.show()
        # return
    
    setup(figsize=(12,6), subplt=(1,2,1))
    x,y = map(np.array,zip(*out))
    print x,y
    pylab.plot(x,y)
    a,b = np.polyfit(x,y,1)
    pylab.plot(x, b+a*x)
    setup(subplt=(1,2,2))
    diff = y-(b+a*x)
    pylab.hist(diff, np.arange(-5,5,0.4))
    line(x=[np.mean(diff),np.mean(diff)-np.std(diff), np.mean(diff)+np.std(diff)])
    print np.std(diff)
    pylab.show()
        
    
    
    cv2.imshow('window', img)
    cv2.waitKey(0)


def highres():
    
    
    # this does not seem to work?!
    # def set_res(cap, x,y):
    #     cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, int(x))
    #     cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, int(y))
    #     return str(cap.get(cv.CV_CAP_PROP_FRAME_WIDTH)),str(cap.get(cv.CV_CAP_PROP_FRAME_HEIGHT))
    # cap = cv2.VideoCapture(0)
    # x = [160 ,160 ,144 ,160 ,160 ,140 ,160 ,224 ,208 ,240 ,220 ,160 ,208 ,256 ,280 ,240 ,320 ,320 ,256 ,320 ,320 ,320 ,320 ,400 ,320 ,432 ,560 ,400 ,480 ,480 ,400 ,376 ,640 ,480 ,512 ,416 ,640 ,480 ,640 ,512 ,800 ,512 ,640 ,640 ,640 ,480 ,720 ,720 ,640 ,720 ,800 ,600 ,640 ,640 ,768 ,800 ,848 ,854 ,800 ,960 ,832 ,960 ,1024,1024,960 ,1024,960 ,1136,1024,1024,1152,1152,1280,1120,1280,1152,1280,1152,1024,1366,1280,1600,1280,1440,1280]
    # 
    # y = [120, 144, 168, 152, 160, 192, 200, 144, 176, 160, 176, 256, 208, 192, 192, 240, 192, 200, 256, 208, 224, 240, 256, 240, 320, 240, 192, 270, 234, 250, 300, 240, 200, 272, 256, 352, 240, 320, 256, 342, 240, 384, 320, 350, 360, 500, 348, 350, 400, 364, 352, 480, 480, 512, 480, 480, 480, 480, 600, 540, 624, 544,  576,  600, 640,  640, 720,  640,  768,  800,  720,  768,  720,  832,  768,  864,  800,  900,  1024,  768,  854,  768,  960,  900,  1024, ]
    # 
    # for w,h in zip(x,y):
    #     print w,h,set_res(cap, w,h)
    #     break
    
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
    # findcircle()
    # main(findrow2)
    # main()
    test()
    
    # highres()