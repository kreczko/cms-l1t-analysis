'''
From http://code.activestate.com/recipes/577819-deprecated-decorator/
'''

import warnings
import functools

def deprecated(replacement=None):
    def outer(fun):
        msg = "{0} is deprecated".format(fun.__name__)
        if replacement is not None:
            msg += "; use {0} instead".format(replacement)
        if fun.__doc__ is None:
            fun.__doc__ = msg

        @functools.wraps(fun)
        def inner(*args, **kwargs):
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return fun(*args, **kwargs)

        return inner
    return outer
