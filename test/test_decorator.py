"""
Tests that are syntactically impossible on python2.
"""

import unittest
from test._test_decorator_py2 import TestASTorator

try:
    from test._test_decorator_py3 import TestASToratorPy3
except SyntaxError:
    pass


if __name__ == '__main__':
    unittest.main()
