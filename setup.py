# encoding: utf-8
from distutils.core import setup
from distutils.spawn import find_executable

# Generate .rst document for PyPI
try:
    from pypandoc import convert
    long_description = convert('README.md', 'rst')
    with open('README.rst', 'wt') as f:
        f.write(long_description)
except ImportError:
    long_description = None

# invoke distutils
setup(
    name='black-magic',
    version='0.0.1',
    description='Decorator utility that operates on black magic',
    long_description=long_description,
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

