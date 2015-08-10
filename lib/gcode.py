#!/usr/bin/env python
# gcode.py : Parses a gcode file
# [2012.07.31] Mendez
import re, sys, os
from copy import deepcopy
from string import Template
from pprint import pprint
from clint.textui import colored, puts, indent, progress

CMDS='GXYZFEMPIJK'

TEMPLATE='''(UPDATED by ${tag})
(Starting)
${init}
(Starting Location:)
${startpos}

${gcode}

(Finished and Moving back to origin)
${finish}
(DONE)'''
INIT='''\
 G20
 G90
 G00 X0.000 Y0.000 Z0.000
 G00 Z0.100'''
FINISH = '''\
 G00 Z0.100
 G00 X0.000 Y0.000
 G00 Z0.000'''



class GCode(list):
    def __init__(self, gcode, limit=None):
        '''start with a gcode ascii file'''
        self.limit = limit
        if isinstance(gcode, str):
            with open(os.path.expanduser(gcode),'r') as f:
                lines = f.readlines()
                filename = gcode
        else:
            filename = gcode.name
            lines = gcode.readlines()
            gcode.close()
        self.filename = filename
        self.lines = lines
        # self.ready = False

    # def append(self,item):
    #     '''add the next nice to the object'''
    #     if self.ready : self.ready = False
    #     super(GCode, self).append(item)

    def parse(self):
        '''WARNING: By default .parse() grabs only the G## commands for creating toolpaths in some space
        if you need everything use .parseall()'''
        everything = self._parse()
        for item in everything:
            toappend = False
            for cmd in CMDS:
                if cmd in item:
                    toappend=True
            if toappend:
                self.append(item)

    def parseAll(self):
        '''Gets everything so that we can print it back out'''
        everything = self._parse()
        for item in everything:
            self.append(item)

    def _parse(self):
        ''' [INTERNAL] convert the readlines into a parsed set of commands and values'''
        puts(colored.blue('Parsing gCode'))

        comment = r'\(.*?\)'
        whitespace = r'\s'

        #command = r''.join([r'(?P<%s>%s(?P<%snum>-?\d+(?P<%sdecimal>\.?)\d*))?'%(c,c,c,c) for c in CMDS])
        '''
        The result of the above commented line is:
        that command is a new regular expression which prints in the followin way in ipython:
        note the doubles of \ probably have to do with the output
        '(?P<G>G(?P<Gnum>-?\\d+(?P<Gdecimal>\\.?)\\d*))?(?P<X>X(?P<Xnum>-?\\d+(?P<Xdecimal>\\.?)\\d*))?(?P<Y>Y(?P<Ynum>-?\\d+(?P<Ydecimal>\\.?)\\d*))?(?P<Z>Z(?P<Znum>-?\\d+(?P<Zdecimal>\\.?)\\d*))?(?P<M>M(?P<Mnum>-?\\d+(?P<Mdecimal>\\.?)\\d*))?(?P<P>P(?P<Pnum>-?\\d+(?P<Pdecimal>\\.?)\\d*))?(?P<I>I(?P<Inum>-?\\d+(?P<Idecimal>\\.?)\\d*))?(?P<J>J(?P<Jnum>-?\\d+(?P<Jdecimal>\\.?)\\d*))?'
        '''
        #one major concwern is that this ordering is not flexible
        #perhaps G code standards dictate the order of X Y Z I J K F E ... etc
        # maybe it is not necessary to add any flexibility in ordering here
        # the most likely malfunction will be due to F coming before x y z or after x y z
        output = []
        for i,line in enumerate(progress.bar(self.lines)):
            if self.limit is not None and i > self.limit: break
        # for i,line in enumerate(self.lines):
            l = line.strip()
            # find comments, save them, and then remove them
            m = re.findall(comment,l)
            l = re.sub(whitespace+'|'+comment,'',l).strip().upper()
            # l = re.sub(whitespace,'',l).upper()

            # Grab the commands
            #c = re.match(command,l)

            # output commands to a nice dict
            out = {}
            out['index'] = i
            # out['line'] = line
            if m: out['comment'] = m
            for cmd in CMDS:
                #incorporating the definintion of command inside this loop should make it more flexible
                command = r''.join(r'(?P<%s>%s(?P<%snum>-?\d*+(?P<%sdecimal>\.?)\d*))?'%(c,c,c,c))
                c = re.match(command,l)
                if c.group(cmd):
                    # either a float if '.' or a int
                    fcn = float if c.group(cmd+'decimal') else int
                    out[cmd] = fcn(c.group(cmd+'num'))
                    out['index'] = i
            if len(out) > 0:
                output.append(out)
        return output
            #
            # if len(out) > 0:
            #     self.append(out)

    def update(self,tool):
        '''Updates the gcode with a toolpath only does x,y'''
        UPDATE = 'xy'
        for x in tool:
            # print len(x)
            if len(x) == 5:
                # print x
                for u in UPDATE:
                    if u.upper() in self[x[4]]:
                        self[x[4]][u.upper()] = x[UPDATE.index(u)]
                # print self[x[4]]

                    # print self[x[4]],
                    # print u.upper(),
                    # print self[x[4]][u.upper()]
                    # print self[x[4]][u.toupper()]#, x[UPDATE.index(u)]
                    # print self[x[4]][u],x[UPDATE.index(u)]


    def copy(self):
        return deepcopy(self)

    def getGcode(self, tag=__name__, start=None):
        lines = []
        for i,line in enumerate(self):
            l = ''
            for cmd in CMDS:
                if cmd in line:
                    l += (' %s%.3f' if cmd in 'XYZFEIJK' else '%s%02i    ')%(cmd,line[cmd])
            # add in the comments
            if 'comment' in line: l += ' '.join(line['comment'])
            lines.append(l)
        params = dict(gcode='\n'.join(lines),init=INIT,finish=FINISH,tag=tag)
        params['startpos'] = '    G00 X%.3f Y%.3f'%(start[0],start[1]) if start else ''
        return Template(TEMPLATE).substitute(params)
