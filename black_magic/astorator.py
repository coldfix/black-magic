"""
Decorator utility for function decorators that works using ast.

This is intented to be a utility for signature preserving function
decorators.

"""
from __future__ import absolute_import

__all__ = [
    'decompile_argspec',
    'param_names',
    'Scope',
    'add_line_info',
    'wraps',
    'function_decorator',
]

import functools
import ast
import inspect
from .compat import *


def decompile_argspec(argspec, defparam_name):
    """
    Decompile a function argspec as returned by inspect.getfullargspec().

    Returns a tuple (declaration, forward, context), where

        - declaration: parameter list as found in the function definition
        - forward: values of the parameters for forwarding to this function
        - context: dictionary of default parameters used in the declaration

    Example:

    >>> spec = getfullargspec(lambda a, b=1, *args, **kwargs: None)
    >>> decompile_argspec(spec, '_') # doctest: +ELLIPSIS
    (<_ast.arguments ...>, <_ast.Call ...>, {'_': [1]})

    >>> spec = getfullargspec(lambda a, b: None)
    >>> decompile_argspec(spec, '_p') # doctest: +ELLIPSIS
    (<_ast.arguments ...>, <_ast.Call ...>, {'_p': []})

    """
    ctx = { defparam_name: [] }

    # Add a value to the context
    def set_value(value):
        ctx[defparam_name].append(value)
        return ast.Subscript(
                value=ast.Name(id=defparam_name, ctx=ast.Load()),
                slice=ast.Index(value=ast.Num(n=len(ctx[defparam_name])-1)),
                ctx=ast.Load())

    annot = getattr(argspec, 'annotations', {})

    # Add positional parameters and their defaults:
    sig = ast.arguments(
            # positional parameters
            args=[param(arg=arg, annotation=annot.get(arg))
                for arg in (argspec.args or [])],
            defaults=[set_value(val)
                for val in (argspec.defaults or [])],
            # varargs
            vararg=argspec.varargs,
            varargannotation=annot.get(argspec.varargs),
            # keyword arguments
            kwarg=argspec.varkw,
            kwargannotation=annot.get(argspec.varkw),
            # keyword-only arguments
            kwonlyargs=[param(arg=arg, annotation=annot.get(arg))
                for arg in (argspec.kwonlyargs or [])],
            kw_defaults=[set_value(argspec.kwonlydefaults[arg])
                for arg in (argspec.kwonlyargs or [])],
        )
    call = ast.Call(
            func=None,
            args=[ast.Name(id=arg, ctx=ast.Load())
                for arg in (argspec.args or [])],
            keywords=[ast.keyword(arg=arg, value=ast.Name(
                                                id=arg, ctx=ast.Load()))
                for arg in (argspec.kwonlyargs or [])],
            starargs=ast.Name(id=argspec.varargs, ctx=ast.Load())
                if argspec.varargs else None,
            kwargs=ast.Name(id=argspec.varkw, ctx=ast.Load())
                if argspec.varkw else None,
        )
    return sig, call, ctx


def param_names(argspec):
    """
    Iterate over all parameter names used in the argspec.
    """
    for argname in argspec.args:
        yield argname
    if argspec.varargs:
        yield argspec.varargs
    if argspec.kwonlyargs:
        for argname in argspec.kwonlyargs:
            yield argname
    if argspec.varkw:
        for argname in argspec.varkw:
            yield argname

class Scope:
    """
    Keeps track of used names in a particular scope.
    """
    def __init__(self, iterable):
        self.names = [iterable]

    """
    Generate a new name that is not present in the scope.
    """
    def new(self):
        name = '_'
        while name in self.names:
            name += '_'
        self.names.append(name)
        return name


def add_line_info(node, lineno = 1, col_offset = 0):
    """
    Recursively add lineno and col_offset to ast node.

    Returns the number of lines the expression requires.

    >>> add_line_info(ast.For(body=[ast.Call(),ast.Return()]))
    3

    """
    if node is None:
        return 0
    lines = 0
    if isinstance(node, (ast.stmt, ast.expr)):
        node.lineno = lineno
        node.col_offset = col_offset
    if getattr(node, '_fields', None):
        for field in node._fields:
            if field != 'body':
                add_line_info(getattr(node, field, None), lineno, col_offset)
        if 'body' in node._fields:
            body = getattr(node, 'body', None)
            if body:
                for stmt in body:
                    lines += add_line_info(
                            stmt, lineno + lines + 1, col_offset + 4)
    elif isinstance(node, list):
        for expr in node:
            add_line_info(expr, lineno, col_offset)
    return lines + 1


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
    sig, call, ctx = decompile_argspec(argspec, scope.new())
    ctx.update({'__builtins__':__builtins__})

    # add the wrapped function to the scope
    wrapper_name = scope.new()
    ctx[wrapper_name] = wrapper
    call.func = ast.Name(id=wrapper_name, ctx=ast.Load())
    fun_name = scope.new()

    # generate and evaluate the complete expression
    this_is_real_cool = ast.Module(body=[
        ast.FunctionDef(
            name=fun_name,
            args=sig,
            body=[ast.Return(value=call)],
            decorator_list=[],
            returns=None
            )
        ])

    try:
        filename = '<wraps(%s:%s)>' % (inspect.getsourcefile(function), function.__name__)
    except TypeError:
        filename = '<wraps(:%s)>' % function.__name__

    it_should_be_forbidden = compile(
            source=ast.fix_missing_locations(this_is_real_cool),
            filename=filename,
            mode='exec',)
    loc = {}
    exec_compat(it_should_be_forbidden, ctx, loc)

    # call update wrapper to copy standard attributes
    return functools.update_wrapper(loc[fun_name], function)


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

    return functools.update_wrapper(decorate, decorator)

