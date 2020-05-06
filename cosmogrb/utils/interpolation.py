import collections

import numba as nb
from interpolation import interp

spec = collections.OrderedDict()
spec['x'] = nb.float32[:]
spec['y'] = nb.float32[:]
spec['N'] = nb.int32
spec['xmin'] = nb.float32
spec['xmax'] = nb.float32

@nb.experimental.jitclass(spec)
class Interp1D(object):

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.N = len(x)
        self.xmax = x.max()
        self.xmin = x.min()

    def evaluate(self, v):

        out = interp(self.x, self.y, v)

        # set outside bounds to zero

        for i in range(v.shape[0]):
            if v[i] > self.xmax:
                out[i] = 0.
            elif v[i] < self.xmin:
                out[i] = 0.

        return out
