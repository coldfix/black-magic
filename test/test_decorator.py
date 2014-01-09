# encoding: utf-8
"""
Python2 compatible unit tests for black_magic.decorator
"""
__all__ = ['TestASTorator']

import unittest
from black_magic.decorator import wraps
from black_magic.compat import signature


class Util(object):
    def mutate(self, real):
        @wraps(real)
        def fake(*args, **kwargs):
            return ~real(*args, **kwargs)
        self.assertEqual(signature(fake), signature(real))
        self.real = real
        self.fake = fake

    def check_result(self, *args, **kwargs):
        self.assertEqual(~self.real(*args, **kwargs),
                         self.fake(*args, **kwargs))

    def must_fail(self, *args, **kwargs):
        self.assertRaises(TypeError, self.fake, *args, **kwargs)

    def assertIs(self, expr1, expr2):
        """Replacement for missing unittest.assertIs in python2.6."""
        if expr1 is not expr2:
            self.fail('%s is not %s' % (repr(expr1), repr(expr2)))

    def assertIsNot(self, expr1, expr2):
        """Replacement for missing unittest.assertIs in python2.6."""
        if expr1 is expr2:
            self.fail('%s is %s' % (repr(expr1), repr(expr2)))

def hd(d):
    """Get hashable form of dictionary."""
    return frozenset(d.items())


class TestASTorator(unittest.TestCase, Util):
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

