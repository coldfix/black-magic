#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup
from distutils.util import convert_path

# read long_description from README.rst
long_description = None
try:
    long_description = open('README.rst').read()
    long_description += '\n' + open('CHANGES.rst').read()
except IOError:
    pass

try:
    from inspect import signature, Signature, Parameter, BoundArguments
except ImportError:     # python2
    install_requires = ['funcsigs']
else:                   # python3
    install_requires = []


def exec_file(path):
    """Execute a python file and return the `globals` dictionary."""
    namespace = {}
    with open(convert_path(path), 'rb') as f:
        exec(f.read(), namespace, namespace)
    return namespace

metadata = exec_file('black_magic/__init__.py')


# invoke distutils
setup(
    name=metadata['__title__'],
    version=metadata['__version__'],
    description=metadata['__summary__'],
    long_description=long_description,
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    url=metadata['__uri__'],
    license=metadata['__license__'],
    packages=['black_magic'],
    install_requires=install_requires,
    classifiers=metadata['__classifiers__'],
    test_suite='nose.collector',
    tests_require='nose',
)
