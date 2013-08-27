#!/usr/bin/env python
from distutils.core import setup

readme = open('README.rst').read()

setup(name='pygrbl',
      version="0.1",
      
      description='pyGRBL :: A simple way of controlling a CNC with GRBL',
      long_description='', 
      
      author="Alexander Mendez",
      author_email="blue.space@gmail.com",
      url ="https://ajmendez.github.io/pygrbl",
      license='license',
      
      packages = ['pygrbl'],
      scripts = [
          'bin/gcommand',
          'bin/galign',
          'bin/gstream',
          'bin/goptimize',
      ]
     )
