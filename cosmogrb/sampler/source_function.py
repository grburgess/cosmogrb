import abc

import matplotlib.pyplot as plt


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

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """
        plot the latent light curve integrated over energy

        :param time: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        y = [self.energy_integrated_evolution(t) for t in time]

        ax.plot(time, y, **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel("flux")

        return fig

    def display_energy_dependent_light_curve(
        self, time, energy, ax=None, cmap="viridis", **kwargs
    ):
        """
        plot the latent light curve integrated over energy

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

        _, colors = array_to_cmap(energy, cmap=cmap, use_log=True)

        for i, lc in enumerate(grid.T):

            ax.plot(time, lc, color=colors[i], **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel("flux")

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
