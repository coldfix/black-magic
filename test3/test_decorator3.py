# encoding: utf-8
"""
Python3 unit tests for black_magic.decorator
"""

import unittest
from black_magic import decorator
import test_decorator

class test_decompile_argspec(test_decorator.test_decompile_argspec):

    def setUp(self):
        self.sample_fns = dict(
            kwonly  = lambda *, a, b=1: a+2*b,
            combined = lambda a,b=1,*args,c,d=1,**kwargs: a+2*b+3*sum(args)+4*sum(kwargs.values())+5*c+6*d,
            )

        self.sample_args = dict(
            kwonly  = [ ([],{'a':3, 'b':1}), ([],{'a':3}) ],
            combined = [ ([1,2,3],{'c':4}), ([1],{'c':2, 'kw':4}),
                        ([],{'a':1,'b':2,'c':4}) ]
            )

