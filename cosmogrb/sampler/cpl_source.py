

import numpy as np

from cosmogrb.sampler.cpl_functions import (cpl_evolution,
                                            energy_integrated_evolution,
                                            sample_energy, sample_events,
                                            time_integrated_evolution)
from cosmogrb.utils.numba_array import VectorFloat64

from .source_function import SourceFunction


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
            effective_area=self._response.effective_area_packed
        )

    def energy_integrated_evolution(self, time):

        ea = self._response.effective_area_packed

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
            effective_area=self._response.effective_area_packed,
            fmax=fmax,
        )

    def sample_energy(self, times):

        ea = self._response.effective_area_packed

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
