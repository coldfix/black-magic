from __future__ import absolute_import

import decorator
import black_magic.decorator

from test.benchmark import _common

class StandardDecorator(_common.Base):
    def __init__(self):
        self.func = decorator.decorator(_common.wrap)(_common.func)

class BlackMagicDecorator(_common.Base):
    def __init__(self):
        self.func = black_magic.decorator.flatorator(_common.wrap)(_common.func)

if __name__ == '__main__':
    _common.main(StandardDecorator, BlackMagicDecorator)
