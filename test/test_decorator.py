# encoding: utf-8
"""
Python2 compatible unit tests for black_magic.decorator
"""
__all__ = ['TestASTorator']

import unittest
import functools
from test._common import hd, _TestUtil

from black_magic.decorator import wraps, partial

class TestASTorator(unittest.TestCase, _TestUtil):
    """
    Unit tests for the wraps function (uses ASTorator).

    Contains only python2 compatible tests, which means no keyword-only
    arguments, no annotations.

    """
    def test_without_arguments(self):
        """Test function without arguments."""
        def real():
            return hash(())
        self.mutate(real)
        self.check_result()
        self.must_fail(0)
        self.must_fail(a=0)

    def test_positional_arguments(self):
        """Test function with only positional arguments."""
        def real(a, b=1):
            return hash((a,b))
        self.mutate(real)
        self.check_result(0)
        self.check_result(0, 1)
        self.check_result(0, b=1)
        self.check_result(a=0)
        self.check_result(a=0, b=1)
        self.must_fail()
        self.must_fail(b=1)
        self.must_fail(a=0, b=1, c=2)
        self.must_fail(0, 1, 2)

    def test_varargs(self):
        """Test function with only variable length positional arguments."""
        def real(*args):
            return hash((args))
        self.mutate(real)
        self.check_result()
        self.check_result(0)
        self.check_result(0, 1)
        self.check_result(0, 1, 2)
        self.must_fail(a=0)
        self.must_fail(0, b=1)

    def test_kwargs(self):
        """Test function with only variable length keyword arguments."""
        def real(**kwargs):
            return hash((hd(kwargs)))
        self.mutate(real)
        self.check_result()
        self.check_result(a=0)
        self.check_result(a=0, b=1)
        self.check_result(a=0, b=1, c=2)
        self.must_fail(0)
        self.must_fail(0, 1)

    def test_all_argument_kinds(self):
        """Test function with all (python2) kinds of arguments."""
        def real(a, b=1, *args, **kwargs):
            return hash((a,b,args,hd(kwargs)))
        self.mutate(real)
        self.check_result(0)
        self.check_result(0, 1)
        self.check_result(0, 1, 2)
        self.check_result(a=0)
        self.check_result(a=0, b=1)
        self.check_result(a=0, b=1, c=1)
        self.check_result(0, 1, 2, d=1)
        self.must_fail(b=1)
        self.must_fail(b=1, c=1)

    def test_default_value_identity(self):
        """Check that object identity is conserved for default values."""
        x = []
        def real(a = x):
            return a
        @wraps(real)
        def fake(*args, **kwargs):
            return real(*args, **kwargs)
        self.assertIs(fake(), x)
        self.assertIsNot(fake([]), x)

    def test_lambda(self):
        """Test that wrapping works also on a lambda."""
        real = lambda a, b=1, *args, **kwargs: hash((a,b,args,hd(kwargs)))
        self.mutate(real)
        self.check_result(0)
        self.check_result(0, 1)
        self.check_result(0, 1, 2)
        self.check_result(a=0)
        self.check_result(a=0, b=1)
        self.check_result(a=0, b=1, c=1)
        self.check_result(0, 1, 2, d=1)
        self.must_fail(b=1)
        self.must_fail(b=1, c=1)

    def test_instance(self):
        class Real(object):
            def __call__(self, a, b=1, *args, **kwargs):
                return hash((a,b,args,hd(kwargs)))
        self.mutate(Real())
        self.check_result(0)
        self.check_result(0, 1)
        self.check_result(0, 1, 2)
        self.check_result(a=0)
        self.check_result(a=0, b=1)
        self.check_result(a=0, b=1, c=1)
        self.check_result(0, 1, 2, d=1)
        self.must_fail(b=1)
        self.must_fail(b=1, c=1)

    def test_partial(self):
        def orig0(a, b, c, *args, **kwargs):
            return hash((a, b, c, args, hd(kwargs)))
        self.mutate(partial(orig0, 0, a=1))
        self.check_result(c=2, d=5)
        self.check_result(2, 3, 4)
        self.must_fail()
        self.must_fail(a=0, c=2)
        self.must_fail(b=1, c=2)

        self.mutate(partial(orig0, 0, 1))
        self.check_result(2)
        self.check_result(c=2)
        self.check_result(2, 3, d=5)
        self.must_fail()
        self.must_fail(a=1, c=2)

        def orig1(a, b, c):
            return hash((a, b, c))
        self.mutate(partial(orig1, b=1))
        self.check_result(0, 2)
        self.check_result(a=0, c=2)
        self.check_result(0, c=2)
        self.must_fail()
        self.must_fail(2, b=2)
        self.must_fail(0, 2, d=3)

    def test_functools_partial(self):
        def orig0(a, b, c, *args, **kwargs):
            return hash((a, b, c, args, hd(kwargs)))
        p0 = functools.partial(orig0, b=0, a=1)
        w0 = wraps(p0)(p0)
        self.assertEqual(orig0(1, 0, 2, d=5),
                         w0(c=2, d=5))
        self.assertEqual(orig0(1, 0, 2, 3, 4),
                         w0(2, 3, 4))
        self.assertRaises(TypeError, w0)
        self.assertRaises(TypeError, w0, a=0, c=2)
        self.assertRaises(TypeError, w0, b=1, c=2)

        orig1 = orig0
        p1 = functools.partial(orig1, 0, 1)
        w1 = wraps(p1)(p1)
        self.assertEqual(orig1(0, 1, 2),
                         w1(2))
        self.assertEqual(orig1(0, 1, c=2),
                         w1(c=2))
        self.assertEqual(orig1(0, 1, 2, 3, d=5),
                         w1(2, 3, d=5))
        self.assertRaises(TypeError, w1)
        self.assertRaises(TypeError, w1, a=1, c=2)

        def orig2(a, b, c):
            return hash((a, b, c))
        p2 = functools.partial(orig2, b=1)
        w2 = wraps(p2)(p2)
        self.assertEqual(orig2(0, 1, 2),
                         w2(0, 2))
        self.assertEqual(orig2(0, 1, 2),
                         w2(a=0, c=2))
        self.assertEqual(orig2(0, 1, 2),
                         w2(0, c=2))
        self.assertRaises(TypeError, w2)
        self.assertRaises(TypeError, w2, 2, b=2)
        self.assertRaises(TypeError, w2, 0, 2, d=3)
