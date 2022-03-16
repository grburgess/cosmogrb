from typing import Iterable

import numba as nb
import numpy as np

from cosmogrb.sampler.subphoto_functions import (
    energy_integrated_evolution,
    sample_energy,
    sample_events,
    subphoto,
    subphoto_evolution,
    time_integrated_evolution,
)

from .source_function import SourceFunction


class SubPhoto(SourceFunction):
    def __init__(
        self,
        K=1,
        xi_b=1e-6,
        r_i=1e11,
        r_0=1e7,
        gamma=400,
        l_grb=1e54,
        emin=10.0,
        emax=1e4,
        response=None,
    ):

        """TODO describe function

        :param K:
        :type K:
        :param xi_b:
        :type xi_b:
        :param r_i:
        :type r_i:
        :param r_0:
        :type r_0:
        :param gamma:
        :type gamma:
        :param l_grb:
        :type l_grb:
        :param emin:
        :type emin:
        :param emax:
        :type emax:
        :param response:
        :type response:
        :returns:

        """
        # attach variables
        self._K = K
        self._xi_b = xi_b
        self._r_i = r_i
        self._r_0 = r_0
        self._gamma = gamma
        self._l_grb = l_grb

        self._pre_comp_ei = None

        super(SubPhoto, self).__init__(
            emin=emin, emax=emax, index=None, response=response
        )

        self._differential_flux = lambda x: subphoto(
            x, xi_b, r_i, r_0, gamma, l_grb, self._z
        )

    def set_integral_function(self):
        def integral(e_edges):
            diff_fluxes_edges = self._differential_flux(e_edges)

            e1 = e_edges[:-1]
            e2 = e_edges[1:]

            return _trapz(
                np.array([diff_fluxes_edges[:-1], diff_fluxes_edges[1:]]).T,
                np.array([e1, e2]).T,
            )

        self._integral_function = integral

    def evolution(self, energy, time):

        """TODO describe function

        :param energy:
        :type energy:
        :param time:
        :type time:
        :returns:

        """
        # call the numba function for speed
        return subphoto_evolution(
            energy=np.atleast_1d(energy),
            time=np.atleast_1d(time),
            K=self._K,
            xi_b=self._xi_b,
            r_i=self._r_i,
            r_0=self._r_0,
            gamma=self._gamma,
            l_grb=self._l_grb,
            z=self._z,
        )

    def time_integrated_spectrum(self, energy, tmin, tmax):

        """TODO describe function

        :param energy:
        :type energy:
        :param tmin:
        :type tmin:
        :param tmax:
        :type tmax:
        :returns:

        """
        return time_integrated_evolution(
            energy=np.atleast_1d(energy),
            tmin=tmin,
            tmax=tmax,
            K=self._K,
            xi_b=self._xi_b,
            r_i=self._r_i,
            r_0=self._r_0,
            gamma=self._gamma,
            l_grb=self._l_grb,
            effective_area=self._response.effective_area_packed,
            z=self._z,
        )

    def energy_integrated_evolution(self, time):

        ea = self._response.effective_area_packed

        if self._pre_comp_ei is None:
            self._pre_comp_ei = energy_integrated_evolution(
                time=np.atleast_1d(time),
                K=self._K,
                xi_b=self._xi_b,
                r_i=self._r_i,
                r_0=self._r_0,
                gamma=self._gamma,
                l_grb=self._l_grb,
                emin=self._emin,
                emax=self._emax,
                effective_area=ea,
                z=self._z,
                precompute=self._pre_comp_ei,
            )

        return self._pre_comp_ei

    def sample_events(self, tstart, tstop, fmax):

        """TODO describe function

        :param tstart:
        :type tstart:
        :param tstop:
        :type tstop:
        :param fmax:
        :type fmax:
        :returns:

        """

        return sample_events(
            tstart=tstart,
            tstop=tstop,
            K=self._K,
            xi_b=self._xi_b,
            r_i=self._r_i,
            r_0=self._r_0,
            gamma=self._gamma,
            l_grb=self._l_grb,
            emin=self._emin,
            emax=self._emax,
            effective_area=self._response.effective_area_packed,
            fmax=fmax,
            z=self._z,
        )

    def sample_energy(self, times):
        """TODO describe function

        :param times:
        :type times:
        :returns:

        """

        ea = self._response.effective_area_packed

        _ = sample_energy(
            times=times[:2],
            K=self._K,
            xi_b=self._xi_b,
            r_i=self._r_i,
            r_0=self._r_0,
            gamma=self._gamma,
            l_grb=self._l_grb,
            emin=self._emin,
            emax=self._emax,
            effective_area=ea,
            z=self._z,
        )

        return sample_energy(
            times=times,
            K=self._K,
            xi_b=self._xi_b,
            r_i=self._r_i,
            r_0=self._r_0,
            gamma=self._gamma,
            l_grb=self._l_grb,
            emin=self._emin,
            emax=self._emax,
            effective_area=ea,
            z=self._z,
        )


@nb.njit(fastmath=True, cache=False)
def _trapz(x, y):
    return np.trapz(x, y)
