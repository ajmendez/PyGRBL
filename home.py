import sys
from lib import argv
from lib.communicate import Communicate

__DOC__ = 'Setup homing for the machine'

SETUP = '''(Setting up homing)
$17=1 (homing on -- requires reset)
$H
$N0 = (setup Staring block)
G28.1 (Soft abs home position)
G30.1 (Sott adjust position)
G10 L2 P1 X0.5 Y0.5 Z-0.5 (setup G54)

G10 L2 P2 X2.5 Y0.5 Z-0.5 (setup G55)

G28 Z0.3 (rapid to 0.3 and then go home)
'''

RESET = '''(Turning off Homing)
$16=0 (Hard Limits off )
$17=0 (Homing off -- requires reset)
$N1= (clear out)
G28
G10 L2 P1 X0 Y0 Z0 (Reset G54)
G10 L2 P2 X0 Y0 Z0 (Reset G54)

'''



class Home(object):
    def __init__(self):
        # self.serial = 
        pass
    

if __name__ == '__main__':
    options = dict(command=dict(args=['reset'],
                   nargs='?',
                   default=False,
                   help='reset the machine so that it does not home'))
    
    args = argv.arg(description=__DOC__,
                    # getDevice=False,
                    otherOptions=options)
    
    
    with Communicate(args.device, args.speed, timeout=args.timeout,
                     debug=args.debug,
                     quiet=args.quiet) as serial:
        if args.reset:
            for line in RESET.splitlines():
                serial.run(line)
        else:
            for line in SETUP.splitlines():
                serial.run(line)
            
            
        # 
        # if args.command:
        #     print 'win'
    
    