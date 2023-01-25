import functools

import numpy as np
import scipy.integrate as integrate

from cosmogrb.utils.logging import setup_logger

from .sampler import Sampler

logger = setup_logger(__name__)

# @nb.jit(forceobj=True)


class Source(Sampler):
    def __init__(
        self, tstart, tstop, source_function, z, use_plaw_sample=False
    ):

        self._source_function = source_function

        self._use_plaw_sample = use_plaw_sample

        self._energy_grid = np.logspace(
            np.log10(self._source_function.emin),
            np.log10(self._source_function.emax),
            25,
        )

        self._z = z

        # pass on tstart and tstop

        super(Source, self).__init__(tstart=tstart, tstop=tstop)

        self._source_function.set_source(self)

        # precompute fmax by integrating over energy

        if self._source_function.response is not None:

            self._fmax = self._get_energy_integrated_max()

    @property
    def z(self):
        return self._z

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param time:
        :param ax:
        :returns:
        :rtype:

        """

        self._source_function.display_energy_integrated_light_curve(
            time=time, ax=ax, **kwargs
        )

    def display_energy_dependent_light_curve(
        self, time, energy, ax=None, cmap="viridis", **kwargs
    ):
        """FIXME! briefly describe function

        :param time:
        :param energy:
        :param ax:
        :param cmap:
        :returns:
        :rtype:

        """

        self._source_function.display_energy_dependent_light_curve(
            time, energy, ax, cmap, **kwargs
        )

    def display_time_dependent_spectrum(
        self, time, energy, ax=None, cmap="viridis", **kwargs
    ):
        """FIXME! briefly describe function

        :param time:
        :param energy:
        :param ax:
        :param cmap:
        :returns:
        :rtype:

        """

        self._source_function.display_time_dependent_spectrum(
            time, energy, ax, cmap, **kwargs
        )

    def set_response(self, response):
        """
        called if there is no response upon creation
        """
        self._source_function.set_response(response)

        self._fmax = self._get_energy_integrated_max()

    def _get_energy_integrated_max(self):
        """
        return the maximum flux in photon number integrated over the energy
        range

        :param start:
        :param stop:
        :returns:
        :rtype:

        """

        # need to find the energy integrated peak flux
        num_grid_points = 50

        time_grid = np.linspace(self._tstart, self._tstop, num_grid_points)

        fluxes = [
            self._source_function.energy_integrated_evolution(t)
            for t in time_grid
        ]

        return np.max(fluxes)

    # def _propagate_photons(self, photons):
    #     """
    #     scale photon energy due to cosmological redshift
    #     """

    #     return photons# / (1 + self._z)

    def sample_times(self):
        """
        sample the evolution function INTEGRATED
        over energy

        :returns:
        :rtype:

        """

        np.random.seed()

        return self._source_function.sample_events(
            self._tstart, self._tstop, self._fmax
        )

    def sample_photons(self, times):

        np.random.seed()

        photons = self._source_function.sample_energy(times)

        return photons

    def sample_channel(self, photons, response):

        channel = response.digitize(photons)

        return channel
