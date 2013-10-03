# encoding: utf-8
"""
Python3 unit tests for black_magic.decorator
"""
__all__ = ['TestASToratorPy3']

import unittest
from test.test_decorator import Util, hd

class TestASToratorPy3(unittest.TestCase, Util):
    """
    Python3 only tests for black_magic.decorator.wraps (uses AST).

    Contains checks for annotations object identity and keyword-only
    arguments.

    """
    def test_annotations_identity(self):
        """Check that annatotions object identity is preserved."""
        _a, _b, _c, _d, _va, _kw, _return = [], [], [], [], [], [], []
        def real(a:_a, b:_b=1, *va:_va, c:_c, d:_d=1, **kw:_kw) -> _return:
            pass
        self.mutate(real)
        _ = self.fake.__annotations__
        self.assertIs(_['a'], _a)
        self.assertIs(_['b'], _b)
        self.assertIs(_['c'], _c)
        self.assertIs(_['d'], _d)
        self.assertIs(_['va'], _va)
        self.assertIs(_['kw'], _kw)
        self.assertIs(_['return'], _return)

    def test_kwonly_arguments(self):
        """Test function with only keyword-only arguments."""
        def real(*, c, d=1):
            return hash((c,d))
        self.mutate(real)
        self.check_result(c=0)
        self.check_result(c=0, d=1)
        self.must_fail()
        self.must_fail(0)
        self.must_fail(0, 1)
        self.must_fail(d=1)

    def test_all_argument_kinds(self):
        """Test function with all kinds of (python3) arguments."""
        def real(a, b=1, *args, c, d=1, **kwargs):
            return hash((a,b,args,c,d,hd(kwargs)))
        self.mutate(real)
        self.check_result(0, c=4)
        self.check_result(a=0, c=4)
        self.check_result(0, 1, c=4)
        self.check_result(0, b=1, c=4)
        self.check_result(0, 1, 2, 3, c=4)
        self.check_result(0, c=4, d=5)
        self.check_result(0, c=4, d=5, e=6)
        self.check_result(0, 1, 2, 3, c=4, d=5, e=6)
        self.must_fail()
        self.must_fail(0)
        self.must_fail(c=4)
        self.must_fail(a=0)
        self.must_fail(0, 4)
        self.must_fail(0, 4, b=1)


