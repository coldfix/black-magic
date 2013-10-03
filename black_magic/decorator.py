"""
Decorator utility for function decorators.

This is intented to be a utility for signature preserving function
decorators.

"""
__all__ = [
    'decompile_argspec',
    'wraps',
    'function_decorator',
]

import functools
from .compat import getfullargspec
from .common import param_names, Scope


def decompile_argspec(argspec, defparam_name):
    """
    Decompile a function argspec as returned by inspect.getfullargspec().

    Returns a tuple (declaration, forward, context), where
    
        - declaration: parameter list as found in the function definition
        - forward: values of the parameters for forwarding to this function
        - context: dictionary of default parameters used in the declaration

    Example:

    >>> spec = getfullargspec(lambda a, b=1, *args, **kwargs: None)
    >>> decompile_argspec(spec, '_')
    ('a, b=_[0], *args, **kwargs', 'a, b, *args, **kwargs', {'_': [1]})

    >>> spec = getfullargspec(lambda a, b: None)
    >>> decompile_argspec(spec, '_p')
    ('a, b', 'a, b', {'_p': []})

    """
    ctx = { defparam_name: [] }
    decl_params = []
    call_params = []

    # Add a value to the context
    def set_value(value):
        ctx[defparam_name].append(value)
        return '%s[%d]' % (defparam_name, len(ctx[defparam_name]) - 1)
    
    # Add parameter
    def add_param(decl, call):
        decl_params.append(decl)
        call_params.append(call)

    # start by adding the positional arguments without defaults:
    defaults = argspec.defaults or []
    num_required = len(argspec.args) - len(defaults)
    decl_params += argspec.args[:num_required]
    call_params += argspec.args[:num_required]

    # positional arguments with defaults:
    for arg,val in zip(argspec.args[num_required:], defaults):
        add_param("%s=%s" % (arg, set_value(val)), arg)

    # add varargs:
    if argspec.varargs:
        add_param('*'+argspec.varargs, '*'+argspec.varargs)
    # need this if no varargs are given but keywordonly args are present:
    elif argspec.kwonlyargs:
        decl_params.append('*')

    # now add keyword-only arguments (this is specific to python3)
    for kwonlyarg in argspec.kwonlyargs:
        if kwonlyarg in argspec.kwonlydefaults:
            val = argspec.kwonlydefaults[kwonlyarg]
            add_param("%s=%s" % (kwonlyarg, set_value(val)),
                      "%s=%s" % (kwonlyarg, kwonlyarg))
        else:
            add_param(kwonlyarg,
                      "%s=%s" % (kwonlyarg, kwonlyarg))

    # and finally the keyword arguments
    if argspec.varkw is not None:
        add_param('**'+argspec.varkw, '**'+argspec.varkw)

    # concatenate and
    decl = ", ".join(decl_params)
    call = ", ".join(call_params)
    return decl, call, ctx


def wraps(function, wrapper=None):
    """
    Wrap a function and copy its signature.

    >>> def real(a, b=1, *args, **kwargs):
    ...     return "%r %r %r %r" % (a, b, args, kwargs)

    >>> @wraps(real)
    ... def fake(*args, **kwargs):
    ...     return "Fake: " + real(*args, **kwargs)

    >>> assert getfullargspec(fake) == getfullargspec(real)

    >>> def check_fake(real, fake, *args, **kwargs):
    ...     rreal = real(*args, **kwargs)
    ...     rfake = fake(*args, **kwargs)
    ...     assert rfake == "Fake: " + rreal, '%r != %r' % (rreal, rfake)

    >>> check_fake(real, fake, 1, 2, 3, 4, kwonly=5, kwarg=6)

    >>> x = [3]
    >>> def real(first = x): return first
    >>> fake = wraps(real, lambda first: real(first))
    >>> assert fake() is real()

    """
    # defer creation of the actual function wrapper until called again
    # (this is for use as a decorator)
    if wrapper is None:
        return lambda wrapper: wraps(function, wrapper)

    # generate signature and call expressions
    argspec = getfullargspec(function)
    scope = Scope(param_names(argspec))
    sig, call, ctx = decompile_argspec(argspec, scope.reserve('_'))

    # add the wrapped function to the scope
    wrapper_name = scope.reserve('_call')
    ctx[wrapper_name] = wrapper

    # generate and evaluate the complete expression
    never_do_this_at_home = 'lambda %s: %s(%s)' % (sig, wrapper_name, call)
    it_is_evil = eval(never_do_this_at_home, ctx)

    if hasattr(function, '__annotations__'):
        it_is_evil.__annotations__ = function.__annotations__

    # call update wrapper to copy standard attributes
    return functools.update_wrapper(it_is_evil, function)


def function_decorator(decorator):
    """
    Decorator for signature preserving function decorators.

    >>> def mul(first, second = 1):
    ...     return first * second

    >>> @function_decorator
    ... def plus_one(fn):
    ...     return lambda *args, **kwargs: 1 + fn(*args, **kwargs)

    >>> fake = plus_one(mul)
    >>> assert fake(2, 3) == 7
    >>> assert fake(4) == 5

    """
    def decorate(function):
        return wraps(function, decorator(function))

    if hasattr(decorator, '__annotations__'):
        decorate.__annotations__ = decorator.__annotations__

    return functools.update_wrapper(decorate, decorator)

