import numba as nb
import numba_scipy
import numpy as np
from interpolation import interp
from scipy.special import gamma, gammaincc

from cosmogrb.sampler.temporal_functions import norris
from cosmogrb.utils.numba_array import VectorFloat64


@nb.njit(fastmath=True, cache=False)
def cpl(x, alpha, xp, F, a, b):

    if alpha == -2:

        Ec = xp / 0.0001  # TRICK: avoid a=-2

    else:

        Ec = xp / (2 + alpha)

    # Cutoff power law

    # get the intergrated flux

    # Gammaincc does not support quantities
    i1 = gammaincc(2 + alpha, a / Ec) * gamma(2 + alpha)
    i2 = gammaincc(2 + alpha, b / Ec) * gamma(2 + alpha)

    intflux = -Ec * Ec * (i2 - i1)

    # intflux = ggrb_int_cpl(alpha, Ec, a, b)

    erg2keV = 6.24151e8

    norm = F * erg2keV / (intflux)

    log_xc = np.log(Ec)

    log_v = alpha * (np.log(x) - log_xc) - (x / Ec)
    flux = np.exp(log_v)

    # Cutoff power law

    return norm * flux


@nb.njit(fastmath=True, cache=False)
def cpl_evolution(
    energy, time, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax
):
    """
    evolution of the CPL function with time

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

    for n in range(N):

        K = norris(time[n], K=peak_flux, t_start=0.0, t_rise=trise, t_decay=tdecay)

        ep = ep_start / (1 + time[n] / ep_tau)

        for m in range(M):
            out[n, m] = cpl(energy[m], alpha=alpha, xp=ep, F=K, a=emin, b=emax)

    return out


@nb.njit(fastmath=True, cache=False)
def folded_cpl_evolution(
    energy,
    time,
    peak_flux,
    ep_start,
    ep_tau,
    alpha,
    trise,
    tdecay,
    emin,
    emax,
    response,
):

    return interp(
        response[0], response[1], energy
    ) * cpl_evolution(
        energy, time, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax
    )


@nb.njit(fastmath=True, cache=False)
def sample_events(
    emin,
    emax,
    tstart,
    tstop,
    peak_flux,
    ep_start,
    ep_tau,
    alpha,
    trise,
    tdecay,
    effective_area,
    fmax,
):

    time = tstart

    arrival_times = VectorFloat64(0)
    arrival_times.append(time)

    while True:

        time = time - (1.0 / fmax) * np.log(np.random.rand())
        if time > tstop:
            break

        test = np.random.rand()

        vtime = VectorFloat64(0)
        vtime.append(time)

        p_test = (
            energy_integrated_evolution(
                emin,
                emax,
                vtime.arr,
                peak_flux,
                ep_start,
                ep_tau,
                alpha,
                trise,
                tdecay,
                effective_area,
            )
            / fmax
        )

        if test <= p_test:
            arrival_times.append(time)

    return arrival_times.arr


@nb.njit(fastmath=True, cache=False)
def sample_energy(
    times, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax, effective_area
):

    N = times.shape[0]

    egrid = np.power(10, np.linspace(np.log10(emin), np.log10(emax), 500))

    out = np.zeros(N)

    tmps = folded_cpl_evolution(
        egrid,
        times,
        peak_flux,
        ep_start,
        ep_tau,
        alpha,
        trise,
        tdecay,
        emin,
        emax,
        effective_area,
    )

    x = np.empty(1)
    vtime = np.empty(1)
    for i in range(N):

        flag = True

        # the maximum is either at the lower bound or the max effective area

        tmp = tmps[i, :]

        idx = np.argmax(tmp)

        # bump up C just in case

        C = tmp[idx] * 5

        # so this scheme for dealing with the effective area
        # is likely very fragile. The idea is that power law
        # envelope needs to be greater than the function every where

        if alpha == -1.0:
            alpha = -1 + 1e-20

        while True:

            # sample from a power law
            u = np.random.uniform(0, 1)
            x[0] = np.power(
                (np.power(emax, alpha + 1) - np.power(emin, alpha + 1)) * u
                + np.power(emin, alpha + 1),
                1.0 / (alpha + 1.0),
            )

            y = np.random.uniform(0, 1) * C * np.power(x[0] / egrid[idx], alpha)

            # here the vtime is just to trick this into being an array

            vtime[0] = times[i]

            if (
                y
                <= (
                    folded_cpl_evolution(
                        x,
                        vtime,
                        peak_flux,
                        ep_start,
                        ep_tau,
                        alpha,
                        trise,
                        tdecay,
                        emin,
                        emax,
                        effective_area
                    )
                )[0, 0]
            ):

                out[i] = x[0]
                break

    return out


@nb.njit(fastmath=True, cache=False)
def energy_integrated_evolution(
    emin, emax, time, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, effective_area
):

    n_energies = 75

    energy_grid = np.power(10, np.linspace(np.log10(emin), np.log10(emax), n_energies))

    energy_slice = folded_cpl_evolution(
        energy_grid,
        time,
        peak_flux,
        ep_start,
        ep_tau,
        alpha,
        trise,
        tdecay,
        emin,
        emax,
        effective_area,
    )

    return np.trapz(energy_slice[0, :], energy_grid)


@nb.njit(fastmath=True, cache=False)
def time_integrated_evolution(
    tmin,
    tmax,
    energy,
    peak_flux,
    ep_start,
    ep_tau,
    alpha,
    trise,
    tdecay,
    emin,
    emax,
    effective_area,
):

    n_times = 50

    time_grid = np.linspace(tmin, tmax, n_times)

    time_slice = folded_cpl_evolution(
        energy, time_grid, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax, effective_area
    )

    return np.trapz(time_slice[:, 0], time_grid)
