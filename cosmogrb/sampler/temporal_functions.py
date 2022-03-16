import numba as nb
import numpy as np


@nb.njit(fastmath=True, cache=False)
def norris(x, K, t_start, t_rise, t_decay):
    if x > t_start:
        return (
            K
            * np.exp(2 * np.sqrt(t_rise / t_decay))
            * np.exp(-t_rise / (x - t_start) - (x - t_start) / t_decay)
        )
    else:
        return 0.0
