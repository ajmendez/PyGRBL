#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
"""

import serial, time, readline
# import time

# Open grbl serial port
s = serial.Serial('/dev/tty.usbmodem1d11',9600)
s.open()
s.isOpen()

# Wake up grbl
s.write("\r\n\r\n")
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

while True:
  x=raw_input('cmd> ')
  if x.strip() == 'quit' or x.strip() == 'exit':
    s.close()
    exit()
  else:
    s.write(x+'\n')
    out=''
    time.sleep(0.5)
    while s.inWaiting() > 0:
      out += s.read(1)
    if out != '':
      print '\n'.join([' |  ' + o for o in out.splitlines()])
  # grbl_out = s.readline() # Wait for grbl response with carriage return
  # print ' : ' + grbl_out.strip()
  
s.close()


# 
# #!/usr/bin/env python
# """\
# Simple g-code streaming script for grbl
# """
# 
# import serial
# import time
# 
# # Open grbl serial port
# s = serial.Serial('/dev/tty.usbmodem0000',9600)
# 
# # Open g-code file
# f = open('somefile.gcode','r');
# 
# # Wake up grbl
# s.write("\r\n\r\n")
# time.sleep(2)   # Wait for grbl to initialize
# s.flushInput()  # Flush startup text in serial input
# 
# # Stream g-code to grbl
# for line in f:
#     l = line.strip() # Strip all EOL characters for streaming
#     print 'Sending: ' + l,
#     s.write(l + '\n') # Send g-code block to grbl
#     grbl_out = s.readline() # Wait for grbl response with carriage return
#     print ' : ' + grbl_out.strip()
# 
# # Wait here until grbl is finished to close serial port and file.
# raw_input("  Press <Enter> to exit and disable grbl.")
# 
# # Close file and serial port
# f.close()
# s.close()
