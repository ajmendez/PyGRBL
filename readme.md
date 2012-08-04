[pyGRBL]
========

Purpose: Controls the GRBLshield using python for general motion and streaming.


Commands:
---------
Most of these commands should support:


    * -d -- Enable debug serial class
    * -q -- Somewhat quieter operation


    * command.py  -- Send basic commands to grbl
    * align.py    -- Use arrowkeys/a/z to move mill bit
    * stream.py   -- Stream gcode to grbl.
    * optimize.py -- Optimization routine.

    * flatten.py    -- Generate raster gcode script.
    * findheight.py -- Generate a height gcode script


grbl settings:
--------------
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



Extra:
------
    * Mendez_modifier.terminal -- OSX terminal support.

ToDo:
-----
    * Document EVERYTHING.

History:
--------
    * [2011/12] -- Built by Mendez with much drinking and eggnog
    * [2012/01] -- Pushed without documentation to bitbucket.
    * [2012/08] -- Updated documentation and cleaned up.


Repository management:
---------------------

before you start editing you do a
git pull #this syncs the repository to online sources
git status # to ensure no failures and completion of sync

to push and edited file
git add . #this adds all files in current dir to current working changes
git status #this tells you what has been modified and what will be committed
git commit -m "<a message about the nature of the update>" #this commits the file with some notes
git push #this pushes the repository to bit bucket 

