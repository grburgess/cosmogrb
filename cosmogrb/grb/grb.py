import multiprocessing as mp

import coloredlogs, logging
import  cosmogrb.utils.logging

logger = logging.getLogger('cosmogrb.grb')


class GRB(object):
    def __init__(self, name="SynthGRB"):
        """
        A basic GRB

        :param name: 
        :param verbose: 
        :returns: 
        :rtype: 

        """
        self._name = name

        logger.debug(f'created a GRB with name: {name}')
        
        self._lightcurves = []

    def _add_lightcurve(self, lightcurve):

        self._lightcurves.append(lightcurve)

    def go(self, n_cores=8):

        pool = mp.Pool(n_cores)

        pool.map(process_lightcurve, self._lightcurves)
        pool.close()
        pool.join()

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

        self._lightcurves[0].display_energy_dependent_light_curve(
            time=time, energy=energy, ax=ax, cmap=cmap, **kwargs
        )

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param time: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        self._lightcurves[0].display_energy_integrated_light_curve(
            time=time, ax=ax, **kwargs
        )


def process_lightcurve(lc):
    lc.process()
