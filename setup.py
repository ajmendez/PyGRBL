#!/usr/bin/env python
from distutils.core import setup

#readme = open('readme.rst').read()

setup(name='pygrbl',
      version="0.2.2",
      
      description='pyGRBL :: A simple way of controlling a CNC with GRBL',
      long_description='', 
      
      author="Alexander Mendez",
      author_email="blue.space@gmail.com",
      url ="https://www.github.com/ajmendez/pygrbl",
      license='license',
      requires = ['clint',
                  'pyserial',
                  'argparse'],
      packages = ['pygrbl'],
      package_data = {'pygrbl':['*.rst', '*.txt']},
      scripts = [
          'bin/gcommand',
          'bin/galign',
          'bin/gstream',
          'bin/goptimize',
      ]
     )
