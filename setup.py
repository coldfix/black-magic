#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup

# read long_description from README.rst
long_description = None
try:
    long_description = open('README.rst').read()
    long_description += '\n' + open('CHANGES.rst').read()
except IOError:
    pass

# invoke distutils
setup(
    name='black-magic',
    version='0.0.3',
    description='Decorator utility that operates on black magic',
    long_description=long_description,
    author='Thomas Gläßle',
    author_email='t_glaessle@gmx.de',
    url='https://github.com/coldfix/black-magic',
    license='Public Domain',
    packages=['black_magic'],
    install_requires=['funcsigs'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
    test_suite='nose.collector'
)

