[pyGRBL]
========

Purpose: Controls the GRBLshield using python for general motion and streaming.


Commands:
---------
Here is a small list of some of the commands that one might find useful
in this package:

    * command.py   -- Send basic commands to grbl
    * align.py     -- Use arrowkeys/a/z to move mill bit
    * stream.py    -- Stream gcode to grbl.
    * optimize.py  -- Optimization routine.
    * orient.py    -- OpenCV Camera Orientation and Height
    * home.py      -- Enable homing
    * visualize.py -- Visualize the 2D PCB boards

    * flatten.py    -- Generate raster gcode script.
    * findheight.py -- Generate a height gcode script

    Most of these commands should support:

        * -d -- Enable fake serial device to debug



grbl settings:
--------------
These are the settings that work on the old machine: 

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

New Machine 10/13:
 Sending: [$$]
  |  $0 = 755.906 (x, step/mm)
  |  $1 = 755.906 (y, step/mm)
  |  $2 = 755.906 (z, step/mm)
  |  $3 = 50 (step pulse, usec)
  |  $4 = 260.000 (default feed, mm/min)
  |  $5 = 520.000 (default seek, mm/min)
  |  $6 = 128 (step port invert mask, int:10000000)
  |  $7 = 50 (step idle delay, msec)
  |  $8 = 50.000 (acceleration, mm/sec^2)
  |  $9 = 0.050 (junction deviation, mm)
  |  $10 = 0.200 (arc, mm/segment)
  |  $11 = 25 (n-arc correction, int)
  |  $12 = 3 (n-decimals, int)
  |  $13 = 1 (report inches, bool)
  |  $14 = 1 (auto start, bool)
  |  $15 = 0 (invert step enable, bool)



Materials Settings:
-------------------
Plexyglass / Acrylic
    $4 = 520
    $5 = 520
    Mill Depth = 0.010 - 0.020 
    Requires oil
    Drills can be problematic -- best to run one at a time




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
    * [2014/03] -- working on opencv


