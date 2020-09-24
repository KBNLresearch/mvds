#!/usr/bin/env python
"""Setup script for mvds"""

from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'branca',
    'flask',
    'folium',
    'geojson',
    'geojsoncontour',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
]
PYTHON_REQUIRES = '>=3.2'

setup(name='mvds',
      install_requires=INSTALL_REQUIRES,
      python_requires=PYTHON_REQUIRES,
      description='Draw maps using meetjestad+KNMI data',
      author='Willem Jan Faber',
      author_email='willemjan.faber@kb.nl',
      url='https://github.com/KBNLresearch/mvds',
      classifiers=[
          'Programming Language :: Python :: 3',]
     )
