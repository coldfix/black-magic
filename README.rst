black-magic
===========

|Build Status| |Coverage| |Version| |Downloads| |License|

.. |Build Status| image:: https://api.travis-ci.org/coldfix/black-magic.png?branch=master
   :target: https://travis-ci.org/coldfix/black-magic
   :alt: Build Status

.. |Coverage| image:: https://coveralls.io/repos/coldfix/black-magic/badge.png?branch=master
   :target: https://coveralls.io/r/coldfix/black-magic
   :alt: Coverage

.. |Version| image:: https://pypip.in/v/black-magic/badge.png
   :target: https://pypi.python.org/pypi/black-magic/
   :alt: Latest Version

.. |Downloads| image:: https://pypip.in/d/black-magic/badge.png
   :target: https://pypi.python.org/pypi/black-magic/
   :alt: Downloads

.. |License| image:: https://pypip.in/license/black-magic/badge.png
   :target: https://pypi.python.org/pypi/black_magic/
   :alt: License


Metaprogramming modules that operate on black magic!

Currently there is only one module available. However, I am all open for
cool ideas.


black\_magic.decorator
~~~~~~~~~~~~~~~~~~~~~~

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


wraps
-----

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


**WARNING**: Do not use ``wraps`` with ``functools.partial``! It won't
work (if using any keyword bindings).

partial
-------

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

- by leaving the ``func`` argument empty ``partial`` can act as decorator:

  .. code:: python

      >>> @partial(None, bar=0)
      ... def foo(bar):
      ...     print(bar)
      >>> foo()
      0

decorator
---------

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


flatorator
----------

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
^^^^^^^^^^^^^^

Q: This uses ugly ``str`` concat and ``eval`` code, right?

A: No, it uses `abstract syntax trees`_ to do its dynamic code generation.

.. _abstract syntax trees: http://docs.python.org/3.3/library/ast.html?highlight=ast#ast

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

