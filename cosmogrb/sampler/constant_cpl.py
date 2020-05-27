import numba as nb
import numpy as np

from cosmogrb.sampler.cpl_constant_functions import (
    cpl_evolution, energy_integrated_evolution, sample_energy, sample_events,
    time_integrated_evolution)

from .source_function import SourceFunction


class ConstantCPL(SourceFunction):
    def __init__(
        self, peak_flux=1e-6, ep=300.0, alpha=-1.0, emin=10.0, emax=1e4, response=None,
    ):

        # attach variables
        self._peak_flux = peak_flux
        self._ep = ep
        self._alpha = alpha

        assert alpha < 0.0, "the rejection sampler is slow as fuck if alpha is positive"

        super(ConstantCPL, self).__init__(
            emin=emin, emax=emax, index=alpha, response=response
        )

    def evolution(self, energy, time):

        # call the numba function for speed
        return cpl_evolution(
            energy=np.atleast_1d(energy),
            time=np.atleast_1d(time),
            peak_flux=self._peak_flux,
            ep=self._ep,
            alpha=self._alpha,

            emin=self._emin,
            emax=self._emax,
            z=self._z
        )

    def time_integrated_spectrum(self, energy, tmin, tmax):

        return time_integrated_evolution(
            energy=np.atleast_1d(energy),
            tmin=tmin,
            tmax=tmax,
            peak_flux=self._peak_flux,
            ep=self._ep,
            alpha=self._alpha,

            emin=self._emin,
            emax=self._emax,
            effective_area=self._response.effective_area_packed,
            z=self._z
        )

    def energy_integrated_evolution(self, time):

        ea = self._response.effective_area_packed

        return energy_integrated_evolution(
            time=np.atleast_1d(time),
            peak_flux=self._peak_flux,
            ep=self._ep,
            alpha=self._alpha,
            emin=self._emin,
            emax=self._emax,
            effective_area=ea,
            z=self._z
        )

    def sample_events(self, tstart, tstop, fmax):

        return sample_events(
            tstart=tstart,
            tstop=tstop,
            peak_flux=self._peak_flux,
            ep=self._ep,
            alpha=self._alpha,

            emin=self._emin,
            emax=self._emax,
            effective_area=self._response.effective_area_packed,
            fmax=fmax,
            z=self._z
        )

    def sample_energy(self, times):

        ea = self._response.effective_area_packed

        return sample_energy(
            times=times,
            peak_flux=self._peak_flux,
            ep=self._ep,
            alpha=self._alpha,

            emin=self._emin,
            emax=self._emax,
            effective_area=ea,
            z=self._z
        )
