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

    def go(self, n_workers=None):

        if n_workers is None:

            n_workers = cosmogrb_config["multiprocess"]["n_universe_workers"]

        with futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = executor.map(self._grb_wrapper, self._parameter_servers)

    def _grb_wrapper(self):

        NotImplementedError()


class ParameterServer(object):
    def __init__(self, name, ra, dec, z, duration, T0, **kwargs):

        self._parameters = dict(
            name=name, ra=ra, dec=dec, z=z, duration=duration, T0=T0
        )

        for k, v in kwargs.items():

            self._parameters[k] = v

        self._file_path = None

    @property
    def parameters(self):
        return self._parameters

    def set_file_path(self, file_path):

        self._file_path = file_path

    @property
    def file_path(self):
        return self._file_path


class GRBWrapper(object):
    def __init__(self, parameter_server):

        grb = self._grb_type(**parameter_server.parameters)
        grb.go(n_workers=cosmogrb_config["multiprocess"]["n_grb_workers"])
        grb.save(parameter_server.save_file_path)

    def _grb_type(self):

        raise NotImplementedError()
