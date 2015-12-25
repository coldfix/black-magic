"""
Tests that are syntactically impossible on python2.
"""

import sys

try:
    from test.py3.test_decorator import *
except SyntaxError:
    __test__ = False
