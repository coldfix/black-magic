"""
Decorator utility for function decorators that works using ast.

This is intented to be a utility for signature preserving function
decorators.

"""
from __future__ import absolute_import

__all__ = [
    'ASTorator',
    'wraps',
    'decorator'
]

import ast
import inspect
import functools

from .compat import signature, ast_arg, exec_compat, is_identifier
from .common import Scope


class ASTorator(object):
    """
    Decorates wapper functions with a given function signature.

    Uses AST not eval.

    """
    def __init__(self, signature, funcname=None, filename=None):
        self.signature = signature
        self.funcname = funcname
        self.filename = filename

    @classmethod
    def from_function(cls, function):
        try:
            filename = inspect.getsourcefile(function)
        except:
            filename = None
        if is_identifier(function.__name__):
            funcname = function.__name__
        else:
            funcname = None
        return cls(signature(function), funcname, filename)

    def decorate(self, callback):
        """
        Create wrapper that calls function with all its arguments.
        """
        # TODO: check whether the callback has compatible signature

        scope = Scope(self.signature.parameters.keys())
        context = {'__builtins__': __builtins__}

        filename = '<wraps(%s:%s)>' % (self.filename or '?', self.funcname)
        callback_name = scope.reserve('_call')
        context[callback_name] = callback

        # Add a value to the context
        empty = self.signature.empty
        def hasattr(param, attr):
            return not getattr(param, attr, empty) is empty

        def attr(param, attr):
            if hasattr(param, attr):
                return ast.Attribute(
                    value=ast.Name(id=param.name, ctx=ast.Load()),
                    attr=attr,
                    ctx=ast.Load())
            else:
                return None

        params = list(self.signature.parameters.values())
        sig = ast.arguments(
            args=[],
            vararg=None,
            varargannotation=None,
            kwonlyargs=[],
            kwarg=None,
            kwargannotation=None,
            defaults=[],
            kw_defaults=[])
        call = ast.Call(
            func=ast.Name(id=callback_name, ctx=ast.Load()),
            args=[],
            keywords=[],
            starargs=None,
            kwargs=None)

        for param in self.signature.parameters.values():
            context[param.name] = param

            # positional parameters
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                sig.args.append(ast_arg(
                    arg=param.name,
                    annotation=attr(param, 'annotation')))
                call.args.append(ast.Name(id=param.name, ctx=ast.Load()))
                if hasattr(param, 'default'):
                    sig.defaults.append(attr(param, 'default'))

            # keyword only
            elif param.kind == param.KEYWORD_ONLY:
                sig.kwonlyargs.append(ast_arg(
                    arg=param.name,
                    annotation=attr(param, 'annotation')))
                call.keywords.append(ast.keyword(
                    arg=param.name,
                    value=ast.Name(id=param.name, ctx=ast.Load())))
                sig.kw_defaults.append(attr(param, 'default'))

            # varargs
            elif param.kind == param.VAR_POSITIONAL:
                sig.vararg = param.name
                sig.varargannotation = attr(param, 'annotation')
                call.starargs = ast.Name(id=param.name, ctx=ast.Load())

            # kwargs
            elif param.kind == param.VAR_KEYWORD:
                sig.kwarg = param.name
                sig.kwargannotation = attr(param, 'annotation')
                call.kwargs = ast.Name(id=param.name, ctx=ast.Load())

            else:
                raise ValueError("Cannot handle parameter type: %s" % param)

        if hasattr(self.signature, 'return_annotation'):
            retannot_name = scope.reserve('_returns')
            context[retannot_name] = self.signature.return_annotation
            returns = ast.Name(id=retannot_name, ctx=ast.Load())
        else:
            returns = None

        # generate and evaluate the complete expression
        loc = {}
        if self.funcname is None:
            expr = ast.Expression(body=ast.Lambda(
                args=sig,
                body=call
            ))
            code = compile(ast.fix_missing_locations(expr), filename, 'eval')
            return eval(code, context, loc)

        else:
            expr = ast.Module(body=[
                ast.FunctionDef(
                    name=self.funcname,
                    args=sig,
                    body=[ast.Return(value=call)],
                    decorator_list=[],
                    returns=returns)
            ])
            code = compile(ast.fix_missing_locations(expr), filename, 'exec')
            exec_compat(code, context, loc)
            return loc[self.funcname]

    __call__ = decorate


    def decorate_with_boundargspec(self, function):
        """
        Create wrapper that calls function with a BoundArgSpec.
        """
        return NotImplemented

    def decorate_with_boundargs(self, function):
        """
        Create a wrapper that calls function with a BoundArgs.
        """
        return self.decorate(
            lambda *args, **kwargs:
                function(self.signature.bind(*args, **kwargs)))


def wraps(function=None, wrapper=None):
    """
    Wrap a function and copy its signature.

    >>> def real(a, b=1, *args, **kwargs):
    ...     return "%r %r %r %r" % (a, b, args, kwargs)

    >>> @wraps(real)
    ... def fake(*args, **kwargs):
    ...     return "Fake: " + real(*args, **kwargs)

    >>> assert signature(fake) == signature(real)

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
    if function is None:
        return lambda function: wraps(function, wrapper)

    return functools.update_wrapper(
        ASTorator.from_function(function)(wrapper),
        function)


def decorator(decorator):
    """
    Decorator for signature preserving function decorators.

    >>> def mul(first, second = 1):
    ...     return first * second

    >>> @decorator
    ... def plus_one(fn):
    ...     return lambda *args, **kwargs: 1 + fn(*args, **kwargs)

    >>> fake = plus_one(mul)
    >>> assert fake(2, 3) == 7
    >>> assert fake(4) == 5

    """
    @wraps(decorator)
    def decorate(function):
        return wraps(function, decorator(function))
    return decorate

