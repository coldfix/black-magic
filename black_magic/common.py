
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
        self.names = set(iterable)

    def reserve(self, name):
        """Generate a new name that is not present in the scope."""
        while name in self.names:
            name += '_'
        self.names.add(name)
        return name
