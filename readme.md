[pyGRBL]
========

Purpose: Controls the GRBLshield using python for general motion and streaming.


Commands:
---------
Most of these commands should support:


    * -d -- Enable debug serial class
    * -w -- Enable gcodedrawer watch app
    * -b -- [limited] Basic terminal functionality 


    * command.py  -- Send basic commands to grbl, also move functionality.
    * origin.py   -- keystroke origin finder.
    * stream.py   -- Stream gcode to grbl.
    * optimize.py -- Optimization routine.
    
    * flatten.py  -- Generate raster gcode script.

    * bufferstream.py -- an attempt to add an additional buffer layer.


grbl settings:
--------------
    |  $0 = 188.976 (steps/mm x)
    |  $1 = 188.976 (steps/mm y)
    |  $2 = 188.976 (steps/mm z)
    |  $3 = 50 (microseconds step pulse)
    |  $4 = 100.000 (mm/min default feed rate)
    |  $5 = 300.000 (mm/min default seek rate)
    |  $6 = 0.200 (mm/arc segment)
    |  $7 = 160 (step port invert mask. binary = 10100000)
    |  $8 = 15.000 (acceleration in mm/sec^2)
    |  $9 = 0.050 (cornering junction deviation in mm)
    |  '$x=value' to set parameter or just '$' to dump current settings
    |  ok



Extra:
------
    * Mendez_modifier.terminal -- OSX terminal support.

ToDo:
-----
    * figure out readline + curses, or just switch to readline only.
    * Document EVERYTHING.

History:
--------
    * [2011/12] -- Built by Mendez with much drinking and eggnog
    * [2012/01] -- Pushed without documentation to bitbucket.
    