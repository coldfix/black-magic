black-magic
===========

|Build Status| |Coverage| |Version| |Downloads| |Unlicense|

.. |Build Status| image:: https://api.travis-ci.org/coldfix/black-magic.png?branch=master
   :target: https://travis-ci.org/coldfix/black-magic
   :alt: Build Status

.. |Coverage| image:: https://coveralls.io/repos/coldfix/black-magic/badge.png?branch=master
   :target: https://coveralls.io/r/coldfix/black-magic
   :alt: Coverage

.. |Version| image:: http://coldfix.de:8080/v/black-magic/badge.png
   :target: https://pypi.python.org/pypi/black-magic/
   :alt: Latest Version

.. |Downloads| image:: http://coldfix.de:8080/d/black-magic/badge.png
   :target: https://pypi.python.org/pypi/black-magic/
   :alt: Downloads

.. |Unlicense| image:: http://coldfix.de:8080/license/black-magic/badge.svg
   :target: http://unlicense.org/
   :alt: Unlicense


Metaprogramming modules that operate on black magic!

Currently there is only one module available. However, I am all open for
cool ideas.


black_magic.decorator
~~~~~~~~~~~~~~~~~~~~~

This is intended to become a more modern and flexible replacement for the
the well known decorator_ module.  This module benefits an API for more
flexible usage. The behaviour of the decorator_ module can easily be
duplicated.

.. _decorator: https://pypi.python.org/pypi/decorator/3.4.0

For those who don't know the decorator_ module: It can be used to create
wrappers for functions that look identical to the original - a common task
when replacing functions via decorators.

Furthermore, this module makes it possible to create wrappers with modified
signatures. Currently, the only specialized function that is explicitly
dedicated to this purpose is ``partial``. If you are interested in doing
more complex modifications you can pass a dynamically created ``Signature``
to ``wraps``. If you make something useful, please consider contributing
your functionality to this module.


.wraps()
--------

``wraps`` can be used similarly to the standard ``functools.wraps``
function. However, it returns a real function, i.e. something that will
have a useful signature when being inspected with ``help()`` or by other
metaprogramming tools. Furthermore, it knows how to copy the signature
exactly, even remembering object identity of default arguments and
annotations:

.. code:: python

    >>> from black_magic.decorator import wraps

    >>> def real(a=[])
    ...     return a

    >>> @wraps(real)
    ... def fake(*args, **kwargs):
    ...     return args

    >>> fake()[0] is real()
    True
    >>> fake(a=1)
    (1,)


If you want to get real crazy you can even use ast.expr_'s:

.. code:: python

    >>> import ast
    >>> fake = wraps(real)(ast.Num(n=1))
    >>> fake(0)
    1

.. _ast.expr: http://docs.python.org/3.3/library/ast.html?highlight=ast#abstract-grammar


**WARNING**: before using ``functools.partial`` with any of the functions in
this module, make sure to read the warning below!


.partial()
----------

This is similar to the ``functools.partial`` function.

.. code:: python

    >>> from black_magic.decorator import partial

    >>> def real(arg):
    ...     print(arg)
    >>> partial(real, arg=0)()
    0

There are some differences, though:

- this function returns a function object which looks like the input
  function, except for the modified parameters.

- all overwritten parameters are completely removed from the signature. In
  ``functools.partial`` this is true only for arguments bound by position.

- the ``**kwargs`` are stripped first, then ``*args``

  .. code:: python

      >>> partial(lambda a,b,c: (a,b,c), 2, a=1)(3)
      (1, 2, 3)

- by leaving the first argument empty ``partial`` can act as decorator:

  .. code:: python

      >>> @partial(None, 1, bar=0)
      ... def foo(bar, lum):
      ...     return bar, lum
      >>> foo()
      (0, 1)

- Note, that the function returned by ``partial(None, ...)`` is just like
  ``partial``: it can bind additional arguments and you can still leave the
  first parameter unspecified. This has weird properties and should not be
  used in production code, but I thought it would be great to add some
  additional brainfuck, to see where it will go.

**CAUTION:** Iterative invocation of ``partial`` (with ``None`` as first
argument) doesn't hide parameters the same way that ``partial`` applied to
a function does, i.e. you can move bound arguments to the right in later
calls. In code:

.. code:: python

    >>> partial(None, 1)(a=0)(lambda a, b: (a, b))()
    (0, 1)


.metapartial()
--------------

The returned value can be called like ``partial`` bind a function to the
parameters given here. In fact, ``partial = metapartial()``.

Binding further keyword arguments via the returned function will overwrite
keyword parameters of previous bindings with the same name.

.. code:: python

    >>> @metapartial(1, a=0, c=3)
    ... def func(a, b, *args, **kwargs):
    ...     return (a, b, args, kwargs)
    >>> func(2)
    (0, 1, (2,), {'c': 3})


.decorator()
------------

This is the canonic utility to create decorators:

.. code:: python

    >>> from black_magic.decorator import decorator

    >>> @decorator
    ... def plus_one(fn):
    ...     def fake(*args, **kwargs):
    ...         return 1 + fn(*args, **kwargs)
    ...     return fake

    >>> @plus_one
    ... def mul_plus_one(a, b):
    ...     return a * b

    >>> mul_plus_one(2, 3)
    7


.flatorator()
-------------

``flatorator`` imitates the functionality of the well known `decorator`_
module.

.. code:: python

    >>> from black_magic.decorator import flatorator

    >>> @flatorator
    ... def times_two(fn, *args, **kwargs):
    ...     return 2 * fn(*args, **kwargs)

    >>> @times_two
    ... def add_times_two(a, b):
    ...     return a + b

    >>> add_times_two(1, 2)
    6


Under the hood
--------------

Q: This uses ugly ``str`` concat and ``eval`` code, right?

A: No, it uses ugly `abstract syntax tree`_ code to do its dynamic code generation.

.. _abstract syntax tree: http://docs.python.org/3.3/library/ast.html?highlight=ast#ast


WARNING: performance hits incoming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorating a function with the tools in this module is a quite costy
operation, so don't do it very often! Invoking the wrapper is no problem on
the other hand.


WARNING: functools.partial is evil
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Be careful when passing ``functools.partial`` objects into ``.wraps``, or
any black magic functions more generally. ``functools.partial`` features
very unsensible handling of arguments that are bound by keyword. These, and
all subsequent arguments, become keyword-only parameters. Consider the
following example:

.. code:: python

    >>> import functools
    >>> def func(a, b, *args, **kwargs):
    ...     return (a, b, args, kwargs)
    >>> part = functools.partial(func, a=0)
    >>> part(1)
    Traceback (most recent call last):
        ...
    TypeError: func() got multiple values for argument 'a'

Furthermore, note that the ``*args`` parameter becomes completely
inaccessible, forever!

For compatibility between python versions and ease of use, I chose to handle
``functools.partial`` objects as if you had actually used
``black_magic.decorator.partial`` with the same arguments, i.e.:

.. code:: python

    >>> wrap = wraps(part)(part)
    >>> wrap(1, 2, c=3)
    (0, 1, (2,), {'c':3})

Note, the signature imposed by ``.wraps(functools.partial(f))`` is
equivalent to the signature of ``.wraps(.partial(f))``, which might come
unexpected.


Tests
~~~~~

This module has been tested to work on python{2.6, 2.7, 3.2, 3.3} and
PyPy1.9 using `Travis CI`_.

.. _Travis CI: https://travis-ci.org/


License
~~~~~~~

To the extent possible under law, Thomas Gläßle has waived all copyright
and related or neighboring rights to black-magic. This work is published
from: Germany.

To the extent possible under law, the person who associated CC0 with
black-magic has waived all copyright and related or neighboring rights
to black-magic.

You should have received a copy of the CC0 legalcode along with this
work. If not, see http://creativecommons.org/publicdomain/zero/1.0/.

