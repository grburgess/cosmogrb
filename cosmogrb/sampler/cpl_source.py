import numba as nb
import numpy as np
from scipy.special import gammaincc, gamma

from .source import SourceFunction


@nb.njit(fastmath=True)
def norris(x, K, t_start, t_rise, t_decay):
    if x > t_start:
        return (
            K
            * np.exp(2 * np.sqrt(t_rise / t_decay))
            * np.exp(-t_rise / (x - t_start) - (x - t_start) / t_decay)
        )
    else:
        return 0.0


def ggrb_int_cpl(a, Ec, Emin, Emax):

    # Gammaincc does not support quantities
    i1 = gammaincc(2 + a, Emin / Ec) * gamma(2 + a)
    i2 = gammaincc(2 + a, Emax / Ec) * gamma(2 + a)

    return -Ec * Ec * (i2 - i1)


def cpl(x, alpha, xp, F, a, b):

    if alpha == -2:

        Ec = xp / 0.0001  # TRICK: avoid a=-2

    else:

        Ec = xp / (2 + alpha)

    # Cutoff power law

    intflux = ggrb_int_cpl(alpha, Ec, a, b)

    erg2keV = 6.24151e8

    norm = F * erg2keV / (intflux)

    # Cutoff power law

    xec = x / Ec

    flux = np.power(xec, alpha) * np.exp(-xec)

    return norm * flux


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
    ):

        # attach variables
        self._peak_flux = peak_flux
        self._ep_start = ep_start
        self._ep_tau = ep_tau
        self._trise = trise
        self._tdecay = tdecay
        self._alpha = alpha

        assert alpha < 0.0, "the rejection sampler is slow as fuck if alpha is positive"

        super(CPLSourceFunction, self).__init__(emin=emin, emax=emax, index=alpha)

    def evolution(self, energy, time):

        # call the numba function for speed
        return _cpl_evolution(
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


@nb.jit(forceobj=True)
def _cpl_evolution(
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

    out = np.zeros((time.shape[0], energy.shape[0]))

    for i in range(time.shape[0]):

        K = norris(time[i], K=peak_flux, t_start=0.0, t_rise=trise, t_decay=tdecay)

        ep = ep_start / (1 + time[i] / ep_tau)

        out[i, :] = cpl(energy, alpha=alpha, xp=ep, F=K, a=emin, b=emax)

    return out
