import collections
import math
import pickle
from functools import update_wrapper, wraps
from pathlib import Path

import h5py
import numba as nb
import numba_scipy
import numpy as np
from interpolation import interp
from interpolation.splines import eval_linear
from numba import float64, int32
from numba.experimental import jitclass
from scipy.special import gamma, gammaincc

from cosmogrb.sampler.cpl_functions import cpl
from cosmogrb.utils.interpolation import Interp1D, jitpickle
from cosmogrb.utils.numba_array import VectorFloat64
from cosmogrb.utils.package_utils import get_path_of_data_file

file_name = get_path_of_data_file("subphoto.h5")

with h5py.File(file_name, "r") as f:
    
    energies = f["energies"][()]

    parameter_order = f["parameter_order"][()]
    
    grid = np.ascontiguousarray(f["grid"][()])
    
    parameters = collections.OrderedDict()
    
    for k in parameter_order:
        
        parameters[k] = f["parameters"][k][()]


data_shape = tuple([x.shape[0] for x in list(parameters.values())])

_values = tuple([np.array(x) for x in list(parameters.values())])

n_energies = len(energies)


@nb.njit(fastmath=True)
def subphoto(energy, xi_b, r_i, r_0, gamma, l_grb, z):
    
    
    scale = gamma/ (1.+ z)
    
    param_values = np.array([xi_b, r_i, r_0, gamma, l_grb])
    
    log_energies = np.log10(energy).reshape((len(energy),1))
    
    log_interpolations = np.empty(n_energies)
    
    
    for i in range(n_energies):


        # grid_interp = GridInterpolate(np.log10(grid[...,i]).reshape(*data_shape),_values)

                
        # log_interpolations[i] = grid_interp(param_values)
        
        log_interpolations[i] = eval_linear( _values,
                                            np.log10(grid[...,i]).reshape(*data_shape), 
                                            param_values)

    e_tilde = np.log10(energies * scale),

    
    values = np.power(10., eval_linear(e_tilde, log_interpolations, log_energies))
    
    return values / scale



@nb.njit(fastmath=True, cache=False)
def subphoto_evolution(energy, time, K, xi_b, r_i, r_0, gamma, l_grb,  z):
    """
    evolution of the SUBPHOTO function with time

    :param energy:
    :param time:
    :param peak_flux:
    :param ep_start:
    :param ep_tau:
    :param alpha:
    :param trise:
    :param tdecay:
    :param emin:
    :param emax:
    :returns:
    :rtype:

    """

    N = time.shape[0]
    M = energy.shape[0]

    out = np.empty((N, M))

    arg = K * subphoto( energy,  xi_b, r_i, r_0, gamma, l_grb,z)

    for n in range(N):
            out[n, :] = arg
            

    return out


@nb.njit(fastmath=True, cache=False)
def folded_subphoto_evolution(
    energy,
    time,
    K,
    xi_b,
    r_i,
    r_0,
    gamma,
    l_grb,
    response,
    z,
):

    return interp(response[0], response[1], energy) * subphoto_evolution(
        energy, time, K, xi_b, r_i, r_0, gamma, l_grb, z
    )


@nb.njit(fastmath=True, cache=False)
def sample_events(
    emin,
    emax,
    tstart,
    tstop,
    K,
    xi_b,
    r_i,
    r_0,
    gamma,
    l_grb,
    effective_area,
    fmax,
    z,
):

    time = tstart

    arrival_times = VectorFloat64(0)
    arrival_times.append(time)

    vtime = np.empty(1)
    while True:

        time = time - (1.0 / fmax) * np.log(np.random.rand())
        if time > tstop:
            break

        test = np.random.rand()

        vtime[0] = time

        # p_test = (
        #     energy_integrated_evolution(
        #         emin, emax, vtime, K, xi_b, r_i, r_0, gamma, l_grb, effective_area, z
        #     )
        #     / fmax
        # )

        p_test = 1.
        
        if test <= p_test:
            arrival_times.append(time)

    return arrival_times.arr


@nb.njit(fastmath=True, cache=False, parallel=True)
def sample_energy(times, K, xi_b, r_i, r_0, gamma, l_grb, emin, emax, effective_area, z):

    N = times.shape[0]

    egrid = np.power(10., np.linspace(np.log10(emin), np.log10(emax), 50))

    out = np.zeros(N)

    times = np.array([times[1]])

    
    tmps = folded_subphoto_evolution(
        egrid, times, K, xi_b, r_i, r_0, gamma, l_grb, effective_area, z
    )

    tmp = tmps[0, :]

    idx = np.argmax(tmp * egrid**2)

    # bump up C just in case

    C = tmp[idx] * 3
    alpha = -1.1


    x = np.empty(1)
    vtime = np.empty(1)
    for i in nb.prange(N):
        
        

        # the maximum is either at the lower bound or the max effective area

     
        # so this scheme for dealing with the effective area
        # is likely very fragile. The idea is that power law
        # envelope needs to be greater than the function every where

        # if alpha == -1.0:
        #     alpha = -1 + 1e-20

        while True:

            # sample from a power law
            u = np.random.uniform(0, 1)
            x[0] = np.power(
                (math.pow(emax, alpha + 1) - math.pow(emin, alpha + 1)) * u
                + math.pow(emin, alpha + 1),
                1.0 / (alpha + 1.0),

            )

#            x[0] = np.random.uniform(emin, emax)
            
            y = np.random.uniform(0, 1) * C * math.pow(x[0] / egrid[idx], alpha)

            # here the vtime is just to trick this into being an array

            
            
            vtime[0] = times[0]

            if (
                y
                <= (
                    folded_subphoto_evolution(
                        x, vtime, K, xi_b, r_i, r_0, gamma, l_grb, effective_area, z
                    )
                )[0, 0]
            ):

                out[i] = x[0]
                break

    return out


@nb.njit(fastmath=True, cache=False)
def energy_integrated_evolution(
        emin, emax, time, K, xi_b, r_i, r_0, gamma, l_grb, effective_area, z, precompute=None
):


    if precompute is not None:

        return precompute
    
    n_energies = 75

    energy_grid = np.power(10., np.linspace(np.log10(emin), np.log10(emax), n_energies))


    energy_slice = folded_subphoto_evolution(
        energy_grid, time, K,  xi_b, r_i, r_0, gamma, l_grb, effective_area, z
    )

    return np.trapz(energy_slice[0, :], energy_grid)


@nb.njit(fastmath=True, cache=False)
def time_integrated_evolution(
    tmin, tmax, energy,  xi_b, r_i, r_0, gamma, l_grb, effective_area, z
):


    n_times = 5

    time_grid = np.linspace(tmin, tmax, n_times)

    time_slice = folded_subphoto_evolution(
        energy, time_grid,  xi_b, r_i, r_0, gamma, l_grb,  effective_area, z
    )

    
    return np.trapz(time_slice[:, 0], time_grid)
