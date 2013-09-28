# encoding: utf-8
"""
Python 2-3 unit tests for black_magic.decorator

Currently, the only available tests are for decompile_argspec.

"""

import unittest
from black_magic.decorator import getfullargspec, decompile_argspec


class test_decompile_argspec(unittest.TestCase):
    def setUp(self):
        self.sample_fns = dict(
                no_args  = lambda: 0,
                pos_args = lambda a: a,
                def_args = lambda a,b=2: a+2*b,
                varargs  = lambda *args: sum(args),
                kwargs   = lambda **kwargs: sum(kwargs.values()),
                combined = lambda a,b=1,*args,**kwargs: a+2*b+3*sum(args)+4*sum(kwargs.values()),
                )

        self.sample_args = dict(
            no_args  = [ ([],{}) ],
            pos_args = [ ([7],{}), ([], {'a':7}) ],
            def_args = [ ([9,2],{}), ([],{'a':9,'b':2}), ([9],{}), ([9],{'b':2}) ],
            varargs  = [ ([5,2],{}), ([2,5],{}) ],
            kwargs   = [ ([],{'a':7, 'b':3}), ([],{'b':3,'c':7}) ],
            combined = [ ([1,2,3],{'kw':4}), ([1],{'b':2, 'kw':4}),
                        ([],{'a':1,'b':2,'kw':4}) ]
            )

    def recompile(self, fn):
        spec = getfullargspec(fn)
        sig,call,ctx = decompile_argspec(spec, '_')
        expr = 'lambda %s: 1+fn(%s)' % (sig,call)
        ctx['fn'] = fn
        return eval(expr, ctx)

    def test_argspec(self):
        for case in self.sample_fns:
            fn = self.sample_fns[case]
            fake = self.recompile(fn)
            assert getfullargspec(fake) == getfullargspec(fn), "for %s()" % case

    def test_return_value(self):
        for case in self.sample_fns:
            fn = self.sample_fns[case]
            fake = self.recompile(fn)
            for args,kwargs in self.sample_args[case]:
                assert fake(*args, **kwargs) == 1 + fn(*args,**kwargs), 'While calling %s(*%r, **%r)' % (case, args, kwargs)

