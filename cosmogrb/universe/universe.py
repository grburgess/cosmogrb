import abc
import os
import numpy as np
import concurrent.futures as futures


import popsynth
import coloredlogs, logging
import cosmogrb.utils.logging

logger = logging.getLogger("cosmogrb.universe")


def sample_theta_phi(size):
    """
    sample a sphere uniformly

    :param size: 
    :returns: 
    :rtype: 

    """

    theta = 90 - np.rad2deg(np.arccos(1 - 2 * np.random.uniform(0.0, 1.0, size=size)))
    phi = np.rad2deg(np.random.uniform(0, 2 * np.pi, size=size))

    return theta, phi


class Universe(object, metaclass=abc.ABCMeta):
    """Documentation for Universe

    """

    def __init__(self, population, grb_base_name="SynthGRB", save_path="."):

        assert isinstance(population, popsynth.Population)

        self._population = population

        self._grb_base_name = grb_base_name

        self._save_path = save_path

        assert sum(self._population.selection) == len(
            self._population.selection
        ), "The population seems to have had a prior selection on it. This is not good"

        # assign the number of GRBs

        self._n_grbs = len(self._population.selection)

        # build the GRBs

        self._name = [f"{self._grb_base_name}_{i}" for i in range(self._n_grbs)]

        logger.debug(f"The Universe contains {self._n_grbs} GRBs")

        self._local_parameters = {}

        self._parameter_servers = []

        self._process_populations()
        self._contstruct_parameter_servers()

    def _get_sky_coord(self):
        self._dec, self._ra = sample_theta_phi(self._n_grbs)

    def _get_redshift(self):
        self._z = self._population.distances

    def _get_duration(self):
        try:
            self._duration = self._population.duration

        except:

            raise RuntimeError("The population must contain a duration value")

    def _contstruct_parameter_servers(self):

        for i in range(self._n_grbs):
            param_dict = {}

            param_dict["z"] = self._z[i]
            param_dict["ra"] = self._ra[i]
            param_dict["dec"] = self._dec[i]
            param_dict["name"] = self._name[i]
            param_dict["duration"] = self._duration[i]

            # this is temporary
            param_dict["T0"] = 0.0

            for k, v in self._local_parameters.items():

                param_dict[k] = v[i]

            param_server = self._parameter_server_type(**param_dict)

            file_name = os.path.join(self._save_path, f"{self._name[i]}_store.h5")

            param_server.set_file_path(file_name)

            self._parameter_servers.append(param_server)

    def _process_populations(self):
        self._get_sky_coord()
        self._get_redshift()
        self._get_duration()

    def go(self, client=None):

        if client is not None:

            futures = client.map(self._grb_wrapper, self._parameter_servers)
            res = client.gather(futures)

            del futures
            del res

        else:

            res = [self._grb_wrapper(ps, serial=True) for ps in self._parameter_servers]

    @abc.abstractmethod
    def _grb_wrapper(self, parameter_server, serial=False):

        NotImplementedError()

    @abc.abstractmethod
    def _parameter_server_type(self):

        NotImplementedError()


class ParameterServer(object):
    def __init__(self, name, ra, dec, z, duration, T0, **kwargs):
        """FIXME! briefly describe function

        :param name: 
        :param ra: 
        :param dec: 
        :param z: 
        :param duration: 
        :param T0: 
        :returns: 
        :rtype: 

        """

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

    def __repr__(self):

        sep = "\n"

        return sep.join([f"{k}: {v}" for k, v in self._parameters.items()])


class GRBWrapper(object, metaclass=abc.ABCMeta):
    def __init__(self, parameter_server, serial=False):

        # construct the grb

        grb = self._grb_type(**parameter_server.parameters)

        # if we are running this parallel

        if not serial:

            grb.go(client=None, serial=serial)

        # otherwise let the GRB know

        else:

            grb.go(serial=serial)

        grb.save(parameter_server.file_path, clean_up=True)

        del grb

    @abc.abstractmethod
    def _grb_type(self, **kwargs):

        raise NotImplementedError()
