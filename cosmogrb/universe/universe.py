import numpy as np
import concurrent.futures as futures


import popsynth
import coloredlogs, logging
import cosmogrb.utils.logging

from cosmogrb import cosmogrb_config


logger = logging.getLogger("cosmogrb.universe")


def sample_theta_phi(size):
    """
    sample a sphere uniformly

    :param size: 
    :returns: 
    :rtype: 

    """

    theta = np.arccos(1 - 2 * np.random.uniform(0.0, 1.0, size=size))
    phi = np.random.uniform(0, 2 * np.pi, size=size)

    return theta, phi


class Universe(object):
    """Documentation for Universe

    """

    def __init__(self, population):

        assert isinstance(population, popsynth.Population)

        self._population = population

        assert sum(self._population.selection) == len(
            self.population.selection
        ), "The population seems to have had a prior selection on it. This is not good"

        # assign the number of GRBs

        self._n_grbs = len(self.selection)

        logger.debug(f"The Universe contains {self._n_grbs} GRBs")

    def _process_populations(self):

        self._dec, self._ra = sample_theta_phi(self._n_grbs)

    def go(self, n_cores=8):

        with futures.ProcessPoolExecutor(max_workers=n_cores,) as executor:
            executor.map(blow_up_grb, self._grbs)


def blow_up_grb(grb):

    grb.go(n_cores=cosmogrb_config["multiprocess"]["n_grb_workers"])

    return grb
