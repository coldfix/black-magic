from __future__ import print_function
from timeit import default_timer

try:
    xrange
except NameError:
    xrange = range


def func(a, b, c, *args, **kwargs):
    return (a, b, c, args, kwargs)


def wrap(fn, *args, **kwargs):
    return fn(*args, **kwargs)


def timeit(fn, number):
    start = default_timer()
    for i in xrange(number):
        fn()
    return default_timer() - start


class Base(object):

    def __call__(self, *args, **kwargs):
        self.func(0, 1, 2, 3, e=5)

    @classmethod
    def test(cls, number=10000):
        init = timeit(cls, number=number)
        call = timeit(cls(), number=number)
        return (init, call)


def main(*classes):
    for cls in classes:
        print(cls.__name__,)
        print(*cls.test())
    return 0

