[pyGRBL]
========

Purpose: Controls the GRBLshield using python for general motion and streaming.


Commands:
---------
Most of these commands should support:
    # -d -- Enable debug serial class
    # -w -- Enable gcodedrawer watch app
    # -b -- [limited] Basic terminal functionality 


    * command.py  -- Send basic commands to grbl, also move functionality.
    * origin.py   -- keystroke origin finder.
    * stream.py   -- Stream gcode to grbl.
    * optimize.py -- Optimization routine.
    
    * flatten.py  -- Generate raster gcode script.

ToDo:
-----
    * figure out readline + curses, or just switch to readline only.
    * Document EVERYTHING.

History:
--------
    * [2011/12] -- Built by Mendez with much drinking and eggnog
    * [2012/01] -- Pushed without documentation to bitbucket.
    