PROBLEM
  spindle pin out number: is pin D11 in GRBL 0.9
  the hardware that we have is using it on pin D12 which used to be the spindle previosly
  we rewired the terminals on the  breakout board so that the Z lim switch and spindle are swapped
  They swapped the so that the spindle could have a PWM in keeping with this added capacity they have implemented the cutting speed parameter
  This major change comes with the hurtle that the variable "S" for cutting speed is by default zero on boot up
  Setting S to 1000 was enough to keep our relay ON
  "M03 S1000"

PROBLEM
  G01 commands must have a Feed rate defined at least one time before they can be issued
  (ie your first G01 command must have an F<value> as in G01X0Y0Z0F9)

1#NEW CONFIGURATION!!!
 | $0=50 (step pulse, usec)
 | $1=50 (step idle delay, msec)
 | $2=0 (step port invert mask:00000000)
 | $3=4 (dir port invert mask:00000100)
 | $4=0 (step enable invert, bool)
 | $5=0 (limit pins invert, bool)
 | $6=0 (probe pin invert, bool)
 | $10=255 (status report mask:11111111)
 | $11=0.010 (junction deviation, mm)
 | $12=0.002 (arc tolerance, mm)
 | $13=1 (report inches, bool)
 | $20=0 (soft limits, bool)
 | $21=0 (hard limits, bool)
 | $22=0 (homing cycle, bool)
 | $23=0 (homing dir invert mask:00000000)
 | $24=130.000 (homing feed, mm/min)
 | $25=260.000 (homing seek, mm/min)
 | $26=250 (homing debounce, msec)
 | $27=1.000 (homing pull-off, mm)
 | $100=755.906 (x, step/mm)
 | $101=755.906 (y, step/mm)
 | $102=755.906 (z, step/mm)
 | $110=500.000 (x max rate, mm/min)
 | $111=500.000 (y max rate, mm/min)
 | $112=500.000 (z max rate, mm/min)
 | $120=50.000 (x accel, mm/sec^2)
 | $121=50.000 (y accel, mm/sec^2)
 | $122=50.000 (z accel, mm/sec^2)
 | $130=200.000 (x max travel, mm)
 | $131=200.000 (y max travel, mm)
 | $132=200.000 (z max travel, mm)
 | ok


THE LESS OLD CONFIG
 | $0=755.906 (x, step/mm)
 | $1=755.906 (y, step/mm)
 | $2=755.906 (z, step/mm)
 | $3=50 (step pulse, usec)
 | $4=240.000 (default feed, mm/min)
 | $5=240.000 (default seek, mm/min)
 | $6=128 (step port invert mask, int:10000000)
 | $7=50 (step idle delay, msec)
 | $8=50.000 (acceleration, mm/sec^2)
 | $9=0.050 (junction deviation, mm)
 | $10=0.020 (arc, mm/segment)
 | $11=25 (n-arc correction, int)
 | $12=3 (n-decimals, int)
 | $13=1 (report inches, bool)
 | $14=1 (auto start, bool)
 | $15=0 (invert step enable, bool)
 | $16=0 (hard limits, bool)
 | $17=0 (homing cycle, bool)
 | $18=127 (homing dir invert mask, int:01111111)
 | $19=25.000 (homing feed, mm/min)
 | $20=500.000 (homing seek, mm/min)
 | $21=200 (homing debounce, msec)

THE OLD CONFIG
    |  $0 = 188.976 (steps/mm x)
    |  $1 = 188.976 (steps/mm y)
    |  $2 = 188.976 (steps/mm z)
    |  $3 = 100 (microseconds step pulse)
    |  $4 = 130.000 (mm/min default feed rate)
    |  $5 = 260.000 (mm/min default seek rate)
    |  $6 = 0.200 (mm/arc segment)
    |  $7 = 96 (step port invert mask. binary = 1100000)
    |  $8 = 4.000 (acceleration in mm/sec^2)
    |  $9 = 0.050 (cornering junction deviation in mm)
