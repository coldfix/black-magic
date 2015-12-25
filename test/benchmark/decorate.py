from __future__ import absolute_import

import functools
import black_magic.decorator
from test.benchmark import _common


class Functools(_common.Base):

    def __init__(self):
        self._decorator = functools.wraps(_common.wrap)

    def __call__(self):
        self._decorator(_common.func)


class BlackMagicDecorator(_common.Base):

    def __init__(self):
        self._decorator = black_magic.decorator.wraps(_common.wrap)

    def __call__(self):
        self._decorator(_common.func)


if __name__ == '__main__':
    _common.main(Functools, BlackMagicDecorator)
