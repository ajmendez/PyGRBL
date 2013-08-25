[pyGRBL]
========

Purpose: Controls the GRBLshield using python for general motion and streaming.


Commands:
---------
Here is a small list of some of the commands that one might find useful
in this package:

    * command.py  -- Send basic commands to grbl
    * align.py    -- Use arrowkeys/a/z to move mill bit
    * stream.py   -- Stream gcode to grbl.
    * optimize.py -- Optimization routine.

    * flatten.py    -- Generate raster gcode script.
    * findheight.py -- Generate a height gcode script

    Most of these commands should support:

        * -d -- Enable fake serial device to debug



grbl settings:
--------------
These are the settings that work on the machine:

    $0 = 188.976 (steps/mm x)
    $1 = 188.976 (steps/mm y)
    $2 = 188.976 (steps/mm z)
    $3 = 100 (microseconds step pulse)
    $4 = 130.000 (mm/min default feed rate)
    $5 = 260.000 (mm/min default seek rate)
    $6 = 0.200 (mm/arc segment)
    $7 = 96 (step port invert mask. binary = 1100000)
    $8 = 4.000 (acceleration in mm/sec^2)
    $9 = 0.050 (cornering junction deviation in mm)



Extra:
------
    * Mendez_modifier.terminal -- OSX terminal support for keystrokes.

ToDo:
-----
    * Document EVERYTHING.

History:
--------
    * [2011/12] -- Started by Mendez
    * [2012/01] -- Pushed without documentation to bitbucket.
    * [2012/08] -- Updated documentation and cleaned up.
    * [2013/08] -- Switched to github public.


