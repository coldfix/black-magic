#!/usr/bin/env python
# encoding: utf-8

from distutils.core import setup
from distutils.spawn import find_executable

# read long_description from README.rst
try:
    f = open('README.rst')
    long_description = f.read()
    f.close()
except:
    long_description = None

# invoke distutils
setup(
    name='black-magic',
    version='0.0.1',
    description='Decorator utility that operates on black magic',
    author='Thomas Gläßle',
    author_email='t_glaessle@gmx.de',
    url='https://github.com/coldfix/black-magic',
    license='Public Domain',
    packages=[
        'black_magic',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
)

