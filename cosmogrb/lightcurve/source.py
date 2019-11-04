import numpy as np
import scipy.integrate as integrate


from .sampler import Sampler


@njit
def norris(x, K, t_start, t_rise, t_decay):
    if x > t_start:
        return (
            K
            * np.exp(2 * (t_rise / t_decay) ** (1 / 2))
            * np.exp(-t_rise / (x - t_start) - (x - t_start) / t_decay)
        )
    else:
        return 0.0


@jit(forceobj=True)
def source_poisson_generator(tstart, tstop, function, fmax):
    """
    Non-homogeneous poisson process generator
    for a given max rate and time range, this function
    generates time tags sampled from the energy integrated
    lightcurve.
    """
    time = tstart

    arrival_times = [tstart]

    while time < tstop:

        time = time - (1.0 / fmax) * np.log(np.random.rand())
        test = np.random.rand()

        p_test = function(time) / fmax

        if test <= p_test:
            arrival_times.append(time)

    return np.array(arrival_times)


class SourceFunction(object):
    def __init__(self, emin= 10.,  emax = 1.E4):
        """
        The source function in time an energy

        :returns: 
        :rtype: 

        """

        self._emin = emin
        self._emax = emax

        

    def evolution(self, energy, time):

        raise NotImplementedError()

    def energy_integrated_evolution(self, time):
        """
        return the integral over energy at a given time 
        via Simpson's rule

        :param time: the time of the pulse

        :returns: 
        :rtype: 

        """

        ene_grid = np.logspace(np.log10(self._emin), np.log10(self._emax), 11)

        return integrate.sims(self.evolution(ene_grid, time), ene_grid)


class Source(Sampler):
    def __init_(self, tstart, tstop, source_function):


        self._source_function = source_function

        self._fmax = self._get_energy_integrated_max()
        
        
        super(Source, self).__init__(tstart=tstart, tstop=tstop)


    def _get_energy_integrated_max(self, start, stop):
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

        time_grid = np.linspace(tstart, tstop, num_grid_points)

        fluxes= [self._source_function.energy_integrated_evolution(t) for t in time_grid]

        return np.max(fluxes)
        

        
        
        
    def _sample_times(self):

        pass
    
        
