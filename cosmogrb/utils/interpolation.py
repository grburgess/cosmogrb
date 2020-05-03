from interpolation import interp


class Interp1D(object):

    def __init__(self, x, y):

        self._x = x
        self._y = y

    def __call__(self, v):

        return interp(self._x, self._y, v)
