# encoding: utf-8
"""
Python2 compatible unit tests for black_magic.decorator.partial
"""
__all__ = ['TestPartial']

import unittest
import functools
from test._common import hd, _TestBase

from black_magic.decorator import wraps, partial

class TestPartial(unittest.TestCase, _TestBase):

    def test_with_functools_partial(self):
        def orig(a, b, c, *args, **kwargs):
            return (a, b, c, args, kwargs)
        part = functools.partial(orig, b=1)
        wrap = partial(part)
        self.assertEqual(orig(0, 1, 2, 3, 4, d=5),
                         wrap(0, 2, 3, 4, d=5))
        self.assertEqual(orig(0, 1, 2, d=5),
                         wrap(0, c=2, d=5))
        self.assertRaises(TypeError, wrap, 0, 2, b=1)
        self.assertRaises(TypeError, wrap, 0)
