## black-magic

Collection of metaprogramming modules that operate on black magic!

Currently the only available module is:

  - `black_magic.decorator`


### License

To the extent possible under law, Thomas Gläßle has waived all copyright
and related or neighboring rights to black-magic. This work is published
from: Germany.

To the extent possible under law, the person who associated CC0 with
black-magic has waived all copyright and related or neighboring rights
to black-magic.

You should have received a copy of the CC0 legalcode along with this
work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.


### black\_magic.decorator

This is intended to become a more modern and flexible replacement for the
the well known [decorator](https://pypi.python.org/pypi/decorator/3.4.0)
module. This module benefits an API for more flexible usage. The behaviour
of the [decorator](https://pypi.python.org/pypi/decorator/3.4.0) module can
easily be duplicated.

#### Usage

You can use it just like the standard `functools.wraps` function:

```python
>>> from black_magic.decorator import wraps

>>> x = []
>>> def real(a:int, b=x) -> "Returns b":
...     return b

>>> @wraps(real)
... def fake(*args, **kwargs):
...     print("Fake!")
...     return real(*args, **kwargs)
```

This will not only update the docstring of the fake function to look like
the original but generate a wrapper function that has *exactly* the same
signature:

```python
>>> assert fake(1) is x   # check object-identity of default-parameter!
Fake!

>>> from inspect import getfullargspec
>>> assert getfullargspec(fake) == getfullargspec(real)
```

If you want to get real crazy you can even use [ast expr](http://docs.python.org/3.3/library/ast.html?highlight=ast#abstract-grammar)s:

```python
>>> import ast
>>> fake = wraps(real)(ast.Num(n=1))
>>> fake(0)
1
```


#### Under the hood

Q: This uses ugly `eval` code, right?

A: No, it uses [abstract syntax trees](http://docs.python.org/3.3/library/ast.html?highlight=ast#ast) to do its dynamic code generation.


#### Tests

This module has been tested to work on python{2.6, 2.7, 3.2, 3.3} and
PyPy1.9 using [Travis](https://travis-ci.org/).

