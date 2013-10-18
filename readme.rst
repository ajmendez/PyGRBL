[pyGRBL]
========

Purpose: Learning python and controlling a CNC.

* Author: Alexander Mendez 
* Contact: blue.space@gmail.com


Commands:
---------
Here is a small list of some of the commands that one might find useful
in this package:

    * bin/gcommand  -- Send basic commands to grbl
    * bin/galign    -- Use arrowkeys/a/z to move mill bit
    * bin/gstream   -- Stream gcode to grbl.
    * bin/goptimize -- Optimization routine.

    * script/flatten.py    -- Generate raster gcode script.
    * script/findheight.py -- Generate a height gcode script


Extra:
------
    * Mendez_modifier.terminal -- OSX terminal support for nice keystroke handling.


ToDo:
-----
    * Document EVERYTHING.


History:
--------
    * [2011/12] -- Started by Mendez
    * [2012/01] -- Pushed without documentation to bitbucket.
    * [2012/08] -- Updated documentation and cleaned up.
    * [2013/08] -- Switched to github public.

Notes:
------
# python setup.py register
# python setup.py sdist bdist_wininst upload
