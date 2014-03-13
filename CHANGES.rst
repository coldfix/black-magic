Changelog
~~~~~~~~~

0.0.9
-----

- fix signature of ``black_magic.decorator.partial``: remove named
  parameter ``func`` that can prevent binding of the a parameter with the
  same name into ``**kwargs``
- return value of ``partial`` can now be used for further parameter
  (re-)binding if the function was left open. CAREFUL: this might have
  unexpected characteristics, such as moving positional parameters to the
  right in later calls.
- add ``metapartial`` function, that accepts only ``*args, **kwargs`` to be
  bound, while the function to be used can only be specified in a second
  step.
- slightly improve performance of ``black_magic.decorator``. Is now
  approximately the same as the performance of the ``decorator`` module.

0.0.8
-----

- convert all ``functools.partial`` to ``black_magic.partial`` with the same
  parameters.

0.0.7
-----

- partial support for ``functools.partial``

0.0.6
-----

- fix ``functools.update_wrapper`` emulation in ``black_magic.decorator.wraps()``

0.0.5
-----

- add ``black_magic.decorator.partial``

0.0.4
-----

- support any callable to be passed to ``ASTorator.decorate``
- convert README to .rst
