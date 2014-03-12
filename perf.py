from __future__ import print_function

from timeit import default_timer
import functools
import decorator
import black_magic.decorator

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

class StandardDecorator(Base):
    def __init__(self):
        self.func = decorator.decorator(wrap)(func)

class BlackMagicDecorator(Base):
    def __init__(self):
        self.func = black_magic.decorator.flatorator(wrap)(func)

class StandardPartial(Base):
    def __init__(self):
        self.func = functools.partial(func, 0)

class BlackMagicPartial(Base):
    def __init__(self):
        self.func = black_magic.decorator.partial(func, 0)

def main():
    for cls in (StandardDecorator, BlackMagicDecorator,
                StandardPartial, BlackMagicPartial):
        print(cls.__name__,)
        print(*cls.test())

if __name__ == '__main__':
    main()
