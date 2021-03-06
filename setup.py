# -*- coding: utf-8 -*-
"""
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""

from setuptools import setup, find_packages
from os import path, walk


def readme():
    with open('README.md') as f:
        return f.read()

def requirements():
    with open('requirements.txt') as f:
        return f.read().split('\n')


setup(name='ampscan',
      version='0.3.0',
      description=('Package for analysis of '
                   'surface scan data for P&O applications'),
      long_description=readme(),
      author='Joshua Steer',
      author_email='Joshua.Steer@soton.ac.uk',
      license='MIT',
      include_package_data=True,
      packages=find_packages(),
      python_requires='>=3.5',  # Your supported Python ranges
      install_requires=requirements(),
      url = 'https://ampscan.readthedocs.io/en/latest/',
      zip_safe=False,)
