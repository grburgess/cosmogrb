import numba as nb
import numpy as np
from cosmogrb.utils.numba_array import VectorFloat64

@nb.njit()
def source_poisson_generator(tstart, tstop, function, fmax):
    """
    Non-homogeneous poisson process generator
    for a given max rate and time range, this function
    generates time tags sampled from the energy integrated
    lightcurve.
    """
    time = tstart

    arrival_times = VectorFloat64(0)
    arrival_times.append(time)

    while True:

        time = time - (1.0 / fmax) * np.log(np.random.rand())
        if time > tstop:
            break

        test = np.random.rand()

        p_test = function(time) / fmax

        if test <= p_test:
            arrival_times.append(time)

    return arrival_times.arr


@nb.jit(forceobj=True)
def evolution_sampler(times, N, function, grid, emin, emax):

    out = np.zeros(N)

    for i, t in enumerate(times):

        flag = True

        # find the maximum of the function.
        fmax = np.max(function(grid, np.array([t]))[0, :])

        while True:

            test = np.random.uniform(0, fmax)
            x = np.random.uniform(emin, emax)

            if test <= function(np.array([x]), np.array([t]))[0, 0]:

                out[i] = x
                break

    return out


@nb.jit(forceobj=True)
def plaw_evolution_sampler(times, N, function, index, emin, emax, eff_area_max):
    """
    specialized sample for power law like functions for 
    increased speed


    :param times: 
    :param N: 
    :param function: 
    :param index: 
    :param emin: 
    :param emax: 
    :returns: 
    :rtype: 

    """

    egrid = np.logspace(np.log10(emin), np.log10(emax), 500)

    out = np.zeros(N)

    for i in range(N):

        flag = True

        # the maximum is either at the lower bound or the max effective area

        # tmp = [function(emin, times[i])[0, 0], function(eff_area_max, times[i])[0, 0]]

        tmp = function(egrid, times[i])[0, :]

        idx = np.argmax(tmp)

        # bump up C just in case

        C = tmp[idx] * 5

        # so this scheme for dealing with the effective area
        # is likely very fragile. The idea is that power law
        # envelope needs to be greater than the function every where

        if index == -1.0:
            index = -1 + 1e-20

        while True:

            # sample from a power law
            u = np.random.uniform(0, 1)
            x = np.power(
                (np.power(emax, index + 1) - np.power(emin, index + 1)) * u
                + np.power(emin, index + 1),
                1.0 / (index + 1.0),
            )

            y = np.random.uniform(0, 1) * C * np.power(x / egrid[idx], index)

            if y <= function(x, times[i])[0, 0]:

                out[i] = x
                break

    return out

