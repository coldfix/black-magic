# encoding: utf-8
"""
Compatibility wrappers for python2.

Provides replacements for python3 functions for a consistent interface on
both languages.

"""
__all__ = ['getfullargspec', 'FullArgSpec', 'ast_arg', 'exec_compat']


# Python2 has no annotations and kwonly arguments, therefore we need to
# create a version of getargspec that returns dummy variables
try:
    from inspect import getfullargspec, FullArgSpec
except ImportError:
    from inspect import getargspec
    from collections import namedtuple
    FullArgSpec = namedtuple(
            'FullArgSpec', [
                'args', 'varargs',
                'varkw', 'defaults',
                'kwonlyargs', 'kwonlydefaults',
                'annotations'])
    def getfullargspec(fn):
        spec = getargspec(fn)
        return FullArgSpec(
            args=spec.args, varargs=spec.varargs,
            varkw=spec.keywords, defaults=spec.defaults,
            kwonlyargs=[], kwonlydefaults=None,
            annotations={})

# Python3 introduces the new inspect.Signature type which is much easier to
# work with than FullArgSpec.
try:
    from inspect import signature, Signature, Parameter, BoundArguments
except ImportError:
    from funcsigs import signature, Signature, Parameter, BoundArguments


# Python3 ast.arg does not exist in python2 as it has no annotations and
# therefore no need for this extra type. So let's create a simple
# replacement:
try:
    from ast import arg as ast_arg
except ImportError:
    import ast
    def ast_arg(arg, annotation):
        return ast.Name(id=arg, ctx=ast.Param())


def exec_compat(expression, globals, locals=None):
    """
    Compatibility exec function for python2 and python3.

    The python2 exec() statement is bound to the following restriction:

        If exec is used in a function and the function contains a nested
        block with free variables, the compiler will raise a SyntaxError
        unless the exec explicitly specifies the local namespace for the
        exec. (In  other words, "exec  obj" would be illegal,  but "exec
        obj in ns" would be legal.)

        http://www.python.org/dev/peps/pep-0227/

    It seems the 3-tuple form of the exec-statement is not recognized as
    explicitly  specifying the  local namespace  therefore creating  the
    need to call it from an intermediate function without nested scope.

    The  3-tuple   form  of   the  exec   statement  is   mandatory  for
    compatibility between python2 and python3.

    http://docs.python.org/2/reference/simple_stmts.html#the-exec-statement
    http://docs.python.org/3.3/library/functions.html?highlight=exec#exec

    """
    exec(expression, globals, locals)


# Python3 allows unicode characters as identifiers while python2 does not:
import re
try:
    exec("ä=0", {})
    _identifier_regex = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)
except SyntaxError:
    _identifier_regex = re.compile(r"^[^\d\W]\w*\Z")

def is_identifier(name):
    return _identifier_regex.match(name) is not None

