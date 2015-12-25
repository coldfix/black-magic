# encoding: utf-8
"""
Python2 compatible unit tests for black_magic.decorator.partial
"""

import unittest
import functools
from test._common import _TestBase

from black_magic.decorator import wraps, partial

__all__ = [
    'TestPartial',
]


class TestPartial(unittest.TestCase, _TestBase):

    def test_partial_iteration_complete(self):
        def orig(a, b, c, d, *args, **kwargs):
            return (a, b, c, args, kwargs)
        part = partial(None, 'a', b='X')
        wrap = part(orig, 'c', b='b')
        self.assertEqual(orig('a', 'b', 'c', 'd'),
                         wrap(d='d'))
        self.assertEqual(orig('a', 'b', 'c', 'd', 0, e='e'),
                         wrap('d', 0, e='e'))
        self.assertRaises(TypeError, wrap)
        self.assertRaises(TypeError, wrap, 'd', a='a')

    def test_partial_iteration_kw_only(self):
        def orig(a, **kwargs):
            return (a, kwargs)
        part = partial(None, b='X')
        wrap = part(orig, b='b')
        self.assertEqual(orig('a', b='b'),
                         wrap(a='a'))
        self.assertEqual(orig('a', b='b'),
                         wrap('a'))
        self.assertRaises(TypeError, wrap)
        self.assertRaises(TypeError, wrap, 'a', 0)

    def test_partial_iteration_varargs(self):
        def orig(a, b, c, d, *args):
            return (a, b, c, d, args)
        part = partial(None, 'b')
        wrap = part(orig, 'c', a='a')
        self.assertEqual(orig('a', 'b', 'c', 'd', 0),
                         wrap('d', 0))
        self.assertEqual(orig('a', 'b', 'c', 'd'),
                         wrap(d='d'))
        self.assertRaises(TypeError, wrap)
        self.assertRaises(TypeError, wrap, 'd', a='a')

    def test_with_function_complete(self):
        def orig(a, b, c, d, *args, **kwargs):
            return (a, b, c, args, kwargs)
        wrap = partial(orig, 'a', 'c', b='b')
        self.assertEqual(orig('a', 'b', 'c', 'd', e='e'),
                         wrap(d='d', e='e'))
        self.assertEqual(orig('a', 'b', 'c', 'd', 0, e='e'),
                         wrap('d', 0, e='e'))
        self.assertRaises(TypeError, wrap)
        self.assertRaises(TypeError, wrap, 'd', d='d')

    def test_with_function_varargs(self):
        def orig(a, b, c, d, *args):
            return (a, b, c, args)
        wrap = partial(orig, 'a', 'c', b='b')
        self.assertEqual(orig('a', 'b', 'c', 'd'),
                         wrap(d='d'))
        self.assertEqual(orig('a', 'b', 'c', 'd'),
                         wrap('d'))
        self.assertEqual(orig('a', 'b', 'c', 'd', 0, 1),
                         wrap('d', 0, 1))
        self.assertRaises(TypeError, wrap)
        self.assertRaises(TypeError, wrap, e='e')
        self.assertRaises(TypeError, wrap, 'd', e='e')

    def test_with_function_kwargs(self):
        def orig(a, b, c, d, **kwargs):
            return (a, b, c, kwargs)
        wrap = partial(orig, 'a', 'c', b='b')
        self.assertEqual(orig('a', 'b', 'c', 'd', e='e'),
                         wrap(d='d', e='e'))
        self.assertEqual(orig('a', 'b', 'c', 'd', e='e'),
                         wrap('d', e='e'))
        self.assertRaises(TypeError, wrap)
        self.assertRaises(TypeError, wrap, 'd', 0)

    def test_with_functools_partial(self):
        def orig(a, b, c, *args, **kwargs):
            return (a, b, c, args, kwargs)
        part = functools.partial(orig, b='b')
        wrap = partial(part)
        self.assertEqual(orig('a', 'b', 'c', 0, d='d'),
                         wrap('a', 'c', 0, d='d'))
        self.assertEqual(orig('a', 'b', 'c', d='d'),
                         wrap('a', c='c', d='d'))
        self.assertRaises(TypeError, wrap, 'a', 'c', b='b')
        self.assertRaises(TypeError, wrap, 'a')
