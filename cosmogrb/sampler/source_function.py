import abc

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from cosmogrb.utils.array_to_cmap import array_to_cmap


class SourceFunction(object, metaclass=abc.ABCMeta):
    def __init__(self, emin=10.0, emax=1.0e4, index=None, response=None):
        """
        The source function in time an energy

        :returns:
        :rtype:

        """

        self._index = index

        # set a response if needed
        self._response = response
        self._source = None

        self._emin = response.emin
        self._emax = response.emax

    def set_response(self, response):

        self._response = response
        self._emin = response.emin
        self._emax = response.emax

    @property
    def response(self):

        return self._response

    def set_source(self, source):

        self._source = source
        self._z = source.z

    @abc.abstractmethod
    def evolution(self, energy, time):
        """

        must return a matrix (time.shape, energy.shape)

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def energy_integrated_evolution(self, time):
        """
        return the integral over energy at a given time
        via Simpson's rule

        :param time: the time of the pulse

        :returns:
        :rtype:

        """

        pass

        # ene_grid = np.logspace(np.log10(self._emin), np.log10(self._emax), 11)

        # return integrate.simps(self.evolution(ene_grid, time)[0, :], ene_grid)

    @abc.abstractclassmethod
    def time_integrated_spectrum(self, energy, t1, t2):
        """

        :param energy:
        :param t1:
        :param t2:
        :returns:
        :rtype:

        """

        pass

        # time_grid = np.linspace(t1, t2, 50)

        # return integrate.simps(self.evolution(energy, time_grid)[:, 0], time_grid)

    @abc.abstractmethod
    def sample_events(self, tstart, tstop, fmax):

        pass

    @abc.abstractmethod
    def sample_energy(self, times):

        pass

    def display_energy_integrated_light_curve(self, time,ax=None, **kwargs):
        """
        plot the latent light curve integrated over energy
        in the observer frame
        set F_peak is given in burst frame -> peak is in observer frame at F/(1+z^2)

        :param time:
        :param ax:
        :returns:
        :rtype:

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        n_energies = 75

        energy_grid = np.power(
            10.0, np.linspace(np.log10(self._emin*(1+self._z)), np.log10(self._emax*(1+self._z)), n_energies)
        )

        y = np.zeros(len(time))
        for i,t in enumerate(time):
            # flux at index (time, energy)
            energy_slice = self.evolution(energy_grid, t)
            y[i] = np.trapz(energy_slice[0, :]*energy_grid, energy_grid)

        ax.plot(time, y, **kwargs)

        ax.set_xlabel("Time [s]")
        ax.set_ylabel(r"Flux [keV/s/cm$^2$]")

        return fig

    def display_energy_dependent_light_curve(
        self, time, energy, ax=None, cmap="viridis", uselog=True, **kwargs
    ):
        """
        plot the latent light curve for different energies

        :param time:
        :param ax:
        :returns:
        :rtype:

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        # flux at index (time, energy)
        grid = self.evolution(energy, time)

        _, colors = array_to_cmap(energy, cmap=cmap, use_log=uselog)

        cmap = mpl.colormaps[cmap]

        if uselog:
            norm = mpl.colors.LogNorm(vmin=min(energy), vmax=max(energy))
        else:
            norm = mpl.colors.Normalize(vmin=min(energy), vmax=max(energy))

        #Add an axis for colorbar on right
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                    cax=cax, label='Energy [keV]')

        for i, lc in enumerate(grid.T):

            ax.plot(time, lc, color=colors[i], **kwargs)

        ax.set_xlabel("Time [s]")
        ax.set_ylabel("flux")

        return fig

    def display_time_dependent_spectrum(
        self, time, energy, ax=None, cmap="viridis", uselog=False, **kwargs
    ):
        """
        plot the latent nu *F_nu spectrum at different times

        :param time:
        :param ax:
        :returns:
        :rtype:

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        # index (time, flux)
        grid = self.evolution(energy, time)

        _, colors = array_to_cmap(time, cmap=cmap, use_log=uselog)

        cmap = mpl.colormaps[cmap]

        if uselog:
            norm = mpl.colors.LogNorm(vmin=min(time), vmax=max(time))
        else:
            mpl.colors.Normalize(vmin=min(time), vmax=max(time))

        #Add an axis for colorbar on right
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                    cax=cax, label='Time [s]')

        for i, lc in enumerate(grid):

            ax.plot(energy, energy**2*lc, color=colors[i], **kwargs)

        ax.set_xlabel("Energy [keV]")
        ax.set_ylabel(r"$\nu F_{\nu}$ [keV$^2$/s/cm$^2$/keV]")
        ax.set_xscale('log')
        ax.set_yscale('log')

        return fig

    @property
    def index(self):
        return self._index

    @property
    def emin(self):
        return self._emin

    @property
    def emax(self):
        return self._emax
