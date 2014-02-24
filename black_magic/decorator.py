"""
Decorator utility for function decorators that works using ast.

This is intented to be a utility for signature preserving function
decorators.

"""
from __future__ import absolute_import

__all__ = [
    'ASTorator',
    'wraps',
    'decorator',
    'value',
    'flatorator',
    'partial',
]

import ast
import inspect

from . import compat
from . import common


class ASTorator(object):
    """
    Creates wapper functions with specific signature.

    Uses abstract syntax trees for dynamic code generation.

    """
    def __init__(self, signature, funcname=None, filename=None,
                 assign=None, update=None):
        self.signature = signature
        self.funcname = funcname
        self.filename = filename
        self.assign = assign or {}
        self.update = update or {}

    @classmethod
    def from_function(cls, function, signature=None):
        """
        Create a wrapper function generator from the given function.

        Pass ``signature`` if you want to create signatures that are
        different from the signature of ``function``. In this case,
        ``function`` will only be used to copy docstring and other
        information.

        """
        try:
            filename = inspect.getsourcefile(function)
        except:
            filename = None
        if compat.is_identifier(getattr(function, '__name__', '')):
            funcname = function.__name__
        else:
            funcname = None

        assign = dict((attr, getattr(function, attr))
                      for attr in ('__module__', '__name__', '__qualname__',
                                   '__doc__', '__annotations__')
                      if hasattr(function, attr))
        update = {'__dict__': function.__dict__}

        return cls(signature or compat.signature(function),
                   funcname=funcname, filename=filename,
                   assign=assign, update=update)

    def decorate(self, callback):
        """
        Create wrapper for callback.

        The callback may be a function, lambda or any ast.expr.

        """
        # TODO: check whether the callback has compatible signature

        scope = common.Scope(self.signature.parameters.keys())
        context = {'__builtins__': __builtins__}

        filename = '<wraps(%s:%s)>' % (self.filename or '?', self.funcname)
        callback_name = scope.reserve('_call')

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
                sig.args.append(compat.ast_arg(
                    arg=param.name,
                    annotation=attr(param, 'annotation')))
                call.args.append(ast.Name(id=param.name, ctx=ast.Load()))
                if hasattr(param, 'default'):
                    sig.defaults.append(attr(param, 'default'))

            # keyword only
            elif param.kind == param.KEYWORD_ONLY:
                sig.kwonlyargs.append(compat.ast_arg(
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

        # THIS IS SOMEWHAT DANGEROUS, BUT ALSO REALLY COOL:
        if isinstance(callback, ast.expr):
            call = callback

        # custom expression generator
        elif isinstance(callback, Value):
            context[callback_name] = callback.value
            call = callback.ast(callback_name)

        # Functions just get called:
        else:
            context[callback_name] = callback

        # generate and evaluate the complete expression
        loc = {}
        if self.funcname is None:
            expr = ast.Expression(body=ast.Lambda(
                args=sig,
                body=call
            ))
            code = compile(ast.fix_missing_locations(expr), filename, 'eval')
            return self._update(eval(code, context, loc))

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
            compat.exec_compat(code, context, loc)
            return self._update(loc[self.funcname])

    def _update(self, func):
        for k,v in self.assign.items():
            setattr(func, k, v)
        for k,v in self.update.items():
            getattr(func, k).update(v)
        return func

    __call__ = decorate


    def decorate_with_boundargspec(self, function):
        """
        Create wrapper that calls function with a BoundArgSpec.
        """
        raise NotImplementedError()

    def decorate_with_boundargs(self, function):
        """
        Create a wrapper that calls function with a BoundArgs.
        """
        return self.decorate(
            lambda *args, **kwargs:
                function(self.signature.bind(*args, **kwargs)))


def wraps(function=None, wrapper=None, signature=None):
    """
    Wrap a function and copy its signature.

    WARNING: do not use ``functools.partial``s with this function!

    >>> def add(a, b=0):
    ...     return a + b

    >>> @wraps(add)
    ... def add_neg(*args, **kwargs):
    ...     return - add(*args, **kwargs)

    >>> add_neg(1)
    -1
    >>> add_neg(a=2, b=3)
    -5

    Note that all default arguments are conserved even by object identity:

    >>> def real(a=[]):
    ...     return a
    >>> fake = wraps(real, lambda a: real(a))
    >>> fake() is real()
    True

    """
    # defer creation of the actual function wrapper until called again
    # (this is for use as a decorator)
    if wrapper is None:
        return lambda wrapper, signature=signature: wraps(function, wrapper, signature)
    if function is None:
        return lambda function, signature=signature: wraps(function, wrapper, signature)

    return ASTorator.from_function(function, signature=signature)(wrapper)


def decorator(decorator):
    """
    Create signature preserving function decorators.

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

    """
    @wraps(decorator)
    def decorate(function):
        return wraps(function, decorator(function))
    return decorate

def flatorator(flatorator):
    """
    Create flat signature preserving decorators.

    >>> @flatorator
    ... def times_two(fn, *args, **kwargs):
    ...     return 2 * fn(*args, **kwargs)

    >>> @times_two
    ... def add_times_two(a, b):
    ...     return a + b

    >>> add_times_two(1, 2)
    6

    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return flatorator(fn, *args, **kwargs)
        return wrapper
    return decorator


class Value(object):
    def __init__(self, value):
        self.value = value

    def ast(self, value_name):
        return ast.Name(id=value_name, ctx=ast.Load())

def value(val):
    """
    Return a 'callback' value for use with decorate.

    Example:

    >>> def real(a, b = 1, *args, **kwargs):
    ...     return None
    >>> fake = wraps(real)(value(2.2))
    >>> fake(0) == 2.2
    True

    >>> fake = wraps(real)(value("Hello world!"))
    >>> fake(a=0)
    'Hello world!'

    >>> x = []
    >>> fake = wraps(real)(value(x))
    >>> assert fake(0) is x

    """
    t = type(val)
    if t is int or t is float:
        return ast.Num(n=val)
    elif t is str:
        return ast.Str(s=val)
    elif t is bytes:
        return ast.Bytes(s=val)
    else:
        return Value(val)



class _ParameterBinding(object):
    def __init__(self,
                 parameters,
                 pos, kw,
                 var_pos, var_kw,
                 bound_args, bound_kwargs):
        self._parameters = parameters
        self._pos = pos
        self._kw = kw
        self._var_pos = var_pos
        self._var_kw = var_kw
        self.args = bound_args
        self.kwargs = bound_kwargs

    @classmethod
    def from_signature(cls, signature):
        parameters = list(signature.parameters.values())
        pos = []
        kw = {}
        var_pos = None
        var_kw = None
        for i,par in enumerate(parameters):
            if par.kind in (par.POSITIONAL_OR_KEYWORD, par.POSITIONAL_ONLY):
                pos.append(i)
            if par.kind in (par.POSITIONAL_OR_KEYWORD, par.KEYWORD_ONLY):
                kw[par.name] = i
            if par.kind == par.VAR_POSITIONAL:
                var_pos = par
            if par.kind == par.VAR_KEYWORD:
                var_kw = par
        return cls(parameters, pos, kw, var_pos, var_kw,
                   [parameters[i].default for i in pos],
                   dict((p.name,p.default) for p in parameters
                        if p.kind == p.KEYWORD_ONLY and p.default is not p.empty))

    def bind(self, *args, **kwargs):
        pos = list(self._pos)
        kw = dict(self._kw.items())
        bound_args = list(self.args)
        bound_kwargs = dict(self.kwargs.items())

        # bind **kwargs:
        for key,val in kwargs.items():
            try:
                index = kw.pop(key)
            except KeyError:          # var_kw
                if self._var_kw is None:
                    raise TypeError(
                        "Got an unexpected keyword argument '%s'"
                        % (key,))
                if key in bound_kwargs:
                    raise TypeError(
                        "Got multiple values for keyword argument '%s'"
                        % (key,))
                bound_kwargs[key] = val
            else:
                try:
                    pos.remove(index)
                except ValueError:
                    bound_kwargs[key] = val
                else:
                    bound_args[index] = val

        # bind *args:
        for index,val in zip(pos, args):
            bound_args[index] = val
            kw.pop(self._parameters[index].name, None)
        num_args = min(len(pos), len(args))
        pos = pos[num_args:]
        args = args[num_args:]
        if args:
            if self._var_pos is None:
                raise TypeError(
                    "%Got too many positional arguments.")
            bound_args += list(args)

        return _ParameterBinding(
            self._parameters,
            pos, kw,
            self._var_pos, self._var_kw,
            bound_args, bound_kwargs)

    def finalize(self):
        if self._kw:
            raise TypeError("Unresolved keyword parameter(s): " +
                            ", ".join(self._kw))
        if self._pos:
            raise TypeError("Not enough parameters...")

    @property
    def free_parameters(self):
        return [p for i,p in enumerate(self._parameters)
                if (i in self._pos or p.name in self._kw or
                    p is self._var_pos or p is self._var_kw)]


def partial(func=None, *args, **kwargs):
    """
    Create a partial that exactly looks like the original.

    There are some important differences to functools.partial:

    - this function returns a function object which looks like the input
      function, except for the modified parameters.

    - all overwritten parameters are completely removed from the signature.
      In functools.partial this is true only for arguments bound by position.

    - the **kwargs are stripped first, then *args

        >>> partial(lambda a,b,c: (a,b,c), 2, a=1)(3)
        (1, 2, 3)

    - by leaving the func argument empty it can act as decorator:

        >>> @partial(None, bar=0)
        ... def foo(bar):
        ...     print(bar)
        >>> foo()
        0

    **NOTE:** Duplicating the behaviour of functools.partial cannot be done
    for the sake of python2 compatibility: binding positional arguments by
    keyword with functools.partial makes them effectively keyword-only
    parameters, which is not natively supported in python2.

    **CAUTION:** Removing parameters from the signature might have unexpected
    side effects like a parameter being passed multiple times (once in the
    kwargs, once regularly).

    """
    if func is None:
        return lambda func: partial(func, *args, **kwargs)

    # NOTE: we can't just use functools.partial/sig.bind_partial to create
    # the underlying wrapper function/argument binding, because it behaves
    # differently for positional arguments when specifying parameters by
    # keyword. (TypeError: multiple values for argument 'xxx')

    sig = compat.signature(func)
    par_binding = _ParameterBinding.from_signature(sig).bind(*args, **kwargs)
    new_sig = sig.replace(parameters=par_binding.free_parameters)

    def wrapper(*call_args, **call_kwargs):
        call_binding = par_binding.bind(*call_args, **call_kwargs)
        call_binding.finalize()
        return func(*call_binding.args, **call_binding.kwargs)

    return wraps(func, wrapper, signature=new_sig)

