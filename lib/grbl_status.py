#library for parsing grbl's reply to the status request '?'
import re

class GRBL_status():
    def __init__(self):
        self.run=""
        self.idle=""
        self.hold=""
        self.alarm=""
        self.x="nan"
        self.y="nan"
        self.z="nan"
        self.x_work="nan"
        self.y_work="nan"
        self.z_work="nan"
        self.buf="nan"
        self.rx="nan"
        self.lim="nan"
        self.string=""
        #self.comment=""



    def parse_grbl_status(self,line):
        line= re.findall(r'\<[^>]*\>', line)[0]
        self.string=line

        if re.search('Idle', line,flags = re.IGNORECASE):
            self.run=False
            self.idle=True
            self.hold=False
            self.alarm=False

        if re.search('Run', line,flags = re.IGNORECASE):
            self.run=True
            self.idle=False
            self.hold=False
            self.alarm=False

        if re.search('Hold', line,flags = re.IGNORECASE):
            self.run= False
            self.idle=False
            self.hold=True
            self.alarm=False

        if re.search('Alarm', line,flags = re.IGNORECASE):
            self.run= False
            self.idle=False
            self.hold=False
            self.alarm=True



        #just for testing
        #line = '<Hold,MPos:0.000,100.002,0.000,WPos:0.000,100.002,0.000,Buf:0,RX:2,Lim:000>'
        #mpos = re.findall('MPos:\d\.\d*,', line, re.IGNORECASE)

        #mpos = re.findall('MPos:\d*\.\d*,\d*\.\d*,\d*\.\d*,', line, flags = re.IGNORECASE)[0]
        mpos = re.findall('MPos:-?\d*\.\d*,-?\d*\.\d*,-?\d*\.\d*,', line, flags = re.IGNORECASE)[0]

        if mpos:
            mpos= re.sub('MPos:','',mpos, flags = re.IGNORECASE)
            mpos= re.split(',',mpos)
            #mpos= mpos.split(',',mpos)
            self.x=float(mpos[0])
            self.y=float(mpos[1])
            self.z=float(mpos[2])

        #wpos = re.findall('WPos:\d*\.\d*,\d*\.\d*,\d*\.\d*,', line, flags = re.IGNORECASE)[0]
        wpos = re.findall('WPos:-?\d*\.\d*,-?\d*\.\d*,-?\d*\.\d*,', line, flags = re.IGNORECASE)[0]
        if wpos:
            wpos= re.sub('WPos:','',wpos, flags = re.IGNORECASE)
            wpos= re.split(',',wpos)
            #mpos= mpos.split(',',mpos)
            self.x_work=float(wpos[0])
            self.y_work=float(wpos[1])
            self.z_work=float(wpos[2])

        buf = re.findall('Buf:\d*', line, flags = re.IGNORECASE)[0]
        if buf:
            buf= re.sub('Buf:','',buf, flags = re.IGNORECASE)
            self.buf=int(buf)

        rx = re.findall('rx:\d*', line, flags = re.IGNORECASE)[0]
        if rx:
            rx= re.sub('RX:','',rx, flags = re.IGNORECASE)
            self.rx=int(rx)

        lim = re.findall('Lim:\d*', line, flags = re.IGNORECASE)[0]
        if lim:
            lim= re.sub('Lim:','',lim, flags = re.IGNORECASE)
            self.lim=lim
        return self



    def x(self):
        return self.x

    def y(self):
        return self.Y

    def z(self):
        return self.z

    def rx(self):
        return self.rx

    def lim(self):
        return self.lim

    def buf(self):
        return self.buf

    def idle(self):
        return self.idle

    def run(self):
        return self.run

    def hold(self):
        return self.hold

    def alarm(self):
        return self.alarm


    def get_x(self):
        return self.x

    def get_y(self):
        return self.Y

    def get_z(self):
        return self.z

    def get_rx(self):
        return self.rx

    def get_lim(self):
        return self.lim

    def get_buf(self):
        return self.buf

    def is_idle(self):
        return self.idle

    def is_running(self):
        return self.run

    def is_haulted(self):
        return self.hold

    def is_alarmed(self):
        return self.alarm
