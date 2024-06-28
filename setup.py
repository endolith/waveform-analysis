#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='waveform-analysis',
      version='0.1',
      description='A collection of functions and scripts for analyzing '
                  'waveforms, especially audio',
      url='https://github.com/endolith/waveform-analysis',
      author_email='endolith@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
