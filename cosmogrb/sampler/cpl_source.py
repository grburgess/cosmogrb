import numba as nb
import numba_scipy
import numpy as np
from scipy.special import gamma, gammaincc

from cosmogrb.utils.numba_array import VectorFloat64

from .source_function import SourceFunction


@nb.njit(fastmath=True, cache=True)
def norris(x, K, t_start, t_rise, t_decay):
    if x > t_start:
        return (
            K
            * np.exp(2 * np.sqrt(t_rise / t_decay))
            * np.exp(-t_rise / (x - t_start) - (x - t_start) / t_decay)
        )
    else:
        return 0.0


class CPLSourceFunction(SourceFunction):
    def __init__(
        self,
        peak_flux=1e-6,
        ep_start=300.0,
        ep_tau=1.0,
        alpha=-1.0,
        trise=1.0,
        tdecay=2,
        emin=10.0,
        emax=1e4,
        response=None,
    ):

        # attach variables
        self._peak_flux = peak_flux
        self._ep_start = ep_start
        self._ep_tau = ep_tau
        self._trise = trise
        self._tdecay = tdecay
        self._alpha = alpha

        assert alpha < 0.0, "the rejection sampler is slow as fuck if alpha is positive"

        super(CPLSourceFunction, self).__init__(
            emin=emin, emax=emax, index=alpha, response=response
        )

    def evolution(self, energy, time):

        # call the numba function for speed
        return cpl_evolution(
            energy=np.atleast_1d(energy),
            time=np.atleast_1d(time),
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            trise=self._trise,
            tdecay=self._tdecay,
            emin=self._emin,
            emax=self._emax,
        )

    def time_integrated_spectrum(self, energy, tmin, tmax):

        return time_integrated_evolution(
            energy=np.atleast_1d(energy),
            tmin=tmin,
            tmax=tmax,
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            trise=self._trise,
            tdecay=self._tdecay,
            emin=self._emin,
            emax=self._emax,
            effective_area=self._response.effective_area
        )

    def energy_integrated_evolution(self, time):

        ea = self._response.effective_area
        
        return energy_integrated_evolution(
            time=np.atleast_1d(time),
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            trise=self._trise,
            tdecay=self._tdecay,
            emin=self._emin,
            emax=self._emax,
            effective_area=ea
        )

    def sample_events(self, tstart, tstop, fmax):

        return sample_events(
            tstart=tstart,
            tstop=tstop,
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            trise=self._trise,
            tdecay=self._tdecay,
            emin=self._emin,
            emax=self._emax,
            effective_area=self._response.effective_area,
            fmax=fmax,
        )

    def sample_energy(self, times):

        ea = self._response.effective_area
        
        return sample_energy(
            times=times,
            peak_flux=self._peak_flux,
            ep_start=self._ep_start,
            ep_tau=self._ep_tau,
            alpha=self._alpha,
            trise=self._trise,
            tdecay=self._tdecay,
            emin=self._emin,
            emax=self._emax,
            effective_area=ea
        )


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


@nb.njit(fastmath=True, cache=True)
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
def sample_energy(times, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax, effective_area):

    N = times.shape[0]

    egrid = np.power(10,np.linspace(np.log10(emin), np.log10(emax), 500))

    out = np.zeros(N)

    tmps = effective_area.evaluate(egrid) * cpl_evolution(egrid, times,
                                                 peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax)

    x = np.empty(1)
    
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

            # here the i+1 is just to trick this into being an array

            if y <= (effective_area.evaluate(x) * cpl_evolution(x, times[i: i+1], peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax))[0, 0]:

                out[i] = x[0]
                break

    return out


@nb.njit(fastmath=True, cache=False)
def energy_integrated_evolution(
    emin, emax, time, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, effective_area
):

    n_energies = 75

    energy_grid = np.power(10, np.linspace(np.log10(emin), np.log10(emax), n_energies))


    
    
    energy_slice = effective_area.evaluate(energy_grid) * cpl_evolution(
        energy_grid, time, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax
    )

    return np.trapz(energy_slice[0, :], energy_grid)


@nb.njit(fastmath=True, cache=True)
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

    time_slice = effective_area.evaluate(energy) * cpl_evolution(
        energy, time_grid, peak_flux, ep_start, ep_tau, alpha, trise, tdecay, emin, emax
    )

    return np.trapz(time_slice[:, 0], time_grid)


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

        K = norris(time[n], K=peak_flux, t_start=0.0,
                   t_rise=trise, t_decay=tdecay)

        ep = ep_start / (1 + time[n] / ep_tau)

        for m in range(M):
            out[n, m] = cpl(energy[m], alpha=alpha, xp=ep, F=K, a=emin, b=emax)

    return out
