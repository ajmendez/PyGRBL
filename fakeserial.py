class Serial():
    '''I need a a debug serial object.'''
    def __init__(self):
        '''init the fake serial and print out ok'''
        self.waiting=1  # If we are waiting
        self.ichar=0    # index of the character that we are on.
        self.msg='ok'   # the message that we print when we get any command
    
    def __getattr__(self, name):
        print 'DEBUG SERIAL: %s'%(name)
        return self.p
    def p(self,x=None,y=None):
        '''Lambda probably makes this better.'''
        pass
    def write(self, x):
        ''' this is pretty noisy so lets ignore it quietly.'''
        pass
    def read(self, n=1):
        '''Return the message n characters at a time.'''
        if self.ichar < len(self.msg):
            out = self.msg[self.ichar:self.ichar+n]
            self.ichar += n
        else:
            self.ichar = 0
            self.waiting = 0
            out='\n'
        return out
    
    def inWaiting(self):
        '''Are we done pushing out a msg? '''
        out = self.waiting
        if self.waiting == 0:
            self.waiting = 1
        return out