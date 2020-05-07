import collections
import pickle
from functools import update_wrapper, wraps

import numba as nb
import numpy as np
from interpolation import interp
from numba import float64, int32, jitclass


class jitpickler:
    '''
    pickler
    '''

    def __init__(self, jitobj):
        self.__dict__['obj'] = jitobj
        self.__dict__['__module__'] = jitobj.__module__
        self.__dict__['__doc__'] = jitobj.__doc__
        self.__dict__['evaluate'] = jitobj.evaluate

    def __getstate__(self):
        obj = self.__dict__['obj']
        typ = obj._numba_type_
        fields = typ.struct

        return typ.classname, {k: getattr(obj, k) for k in fields}

    def __setstate__(self, state):
        name, value = state
        cls = globals()[name]
        value['_decorator'] = False
        jitobj = cls(**value)
        self.__init__(jitobj)

    def __getattr__(self, attr):
        return getattr(self.__dict__['obj'], attr)

    def __setattr__(self, attr, value):
        return setattr(self.__dict__['obj'], attr, value)

    def __delattr__(self, attr):
        return delattr(self.__dict__['obj'], attr)


def jitpickle(cls):
    decoratorkw = '_decorator'
    @wraps(cls)
    def decorator(*args, **kwargs):
        if kwargs.get(decoratorkw, True):
            kwargs.pop(decoratorkw, None)
            return jitpickler(cls(*args, **kwargs))
        else:
            kwargs.pop(decoratorkw, None)
            return cls(*args, **kwargs)
    return decorator



spec = [("x", nb.float64[:] ),
        ("y", nb.float64[:] ),
        ("xmin", nb.float32 ),
        ("xmax", nb.float32 ),


]


@jitpickle
@nb.experimental.jitclass(spec)
class Interp1D(object):

    def __init__(self, x, y, xmin, xmax):

        self.x = x
        self.y = y
        self.xmax = xmax
        self.xmin = xmin

    def evaluate(self, v):

        out = interp(self.x, self.y, v)

        # set outside bounds to zero

        for i in range(v.shape[0]):
            if v[i] > self.xmax:
                out[i] = 0.
            elif v[i] < self.xmin:
                out[i] = 0.

        return out
