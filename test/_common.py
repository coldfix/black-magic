
from black_magic.decorator import wraps, partial
from black_magic.compat import signature

def hd(d):
    """Get hashable form of dictionary."""
    return frozenset(d.items())

class _TestBase(object):
    def assertIs(self, expr1, expr2):
        """Replacement for missing unittest.assertIs in python2.6."""
        if expr1 is not expr2:
            self.fail('%s is not %s' % (repr(expr1), repr(expr2)))

    def assertIsNot(self, expr1, expr2):
        """Replacement for missing unittest.assertIs in python2.6."""
        if expr1 is expr2:
            self.fail('%s is %s' % (repr(expr1), repr(expr2)))

class _TestUtil(_TestBase):
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

