from __future__ import absolute_import

import functools
import black_magic.decorator
from test.benchmark import _common

class StandardPartial(_common.Base):
    def __init__(self):
        self.func = functools.partial(_common.func, 0)

class BlackMagicPartial(_common.Base):
    def __init__(self):
        self.func = black_magic.decorator.partial(_common.func, 0)

if __name__ == '__main__':
    _common.main(StandardPartial, BlackMagicPartial)
