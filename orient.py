#!/usr/bin/env python
# orient
# determines the orientation of the stock
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
'''

import numpy as np
import pylab
import cv
import cv2





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
    





def main(fcn=None):
    capture = cv.CaptureFromCAM(0)
    cv.WaitKey(200)
    font = cv.InitFont(cv.CV_FONT_HERSHEY_DUPLEX, 1, 1, 0, 2, 8)
    while True:
       frame = cv.QueryFrame(capture)
       
       if fcn:
           frame = fcn(frame)
       
       cv.PutText(frame, "orient.py", (10,460), font, cv.RGB(17, 110, 255))
       cv.Line(frame, (320,0), (320,480) , 255)
       cv.Line(frame, (0,240), (640,240) , 255)
       cv.Circle(frame, (320,240), 100, 255)
   
       cv.ShowImage("Window",frame)
       # c = (cv.WaitKey(16) & 255)
       c = (cv.WaitKey(100) & 255)
   
       if c in [27, 113]: #Break if user enters 'Esc', 'q'.
          break
       elif c != 255:
           print c
       
    
    


if __name__ == "__main__":
    # findcircle()
    main(findrow2)