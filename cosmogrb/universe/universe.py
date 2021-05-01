import abc
import logging
import os

import numpy as np

from cosmogrb.utils.logging import setup_logger

import popsynth
from cosmogrb.universe.survey import Survey


logger = setup_logger(__name__)


class Universe(object, metaclass=abc.ABCMeta):
    """Documentation for Universe

    """

    def __init__(self, population_file, grb_base_name="SynthGRB", save_path="."):
        """



        :param population_file: 
        :param grb_base_name: 
        :param save_path: 
        :returns: 
        :rtype: 

        """

        # we want to store the absolute path so that we can find it later
        self._population_file = os.path.abspath(population_file)

        self._is_processed = False

        self._population = popsynth.Population.from_file(population_file).to_sub_population()

        self._grb_base_name = grb_base_name

        self._save_path = save_path

        assert sum(self._population.selection) == len(
            self._population.selection
        ), "The population seems to have had a prior selection on it. This is not good"

        # assign the number of GRBs

        self._n_grbs = len(self._population.selection)

        # build the GRBs

        self._name = [
            f"{self._grb_base_name}_{i}" for i in range(self._n_grbs)]

        logger.debug(f"The Universe contains {self._n_grbs} GRBs")

        self._local_parameters = {}

        self._parameter_servers = []

        self._process_populations()
        self._contstruct_parameter_servers()

    def _get_sky_coord(self):

        self._ra = np.rad2deg(self._population.phi)
        self._dec = 90 - np.rad2deg(self._population.theta)

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

            file_name = os.path.join(
                self._save_path, f"{self._name[i]}_store.h5")

            param_server.set_file_path(file_name)

            self._parameter_servers.append(param_server)

    def _process_populations(self):
        self._get_sky_coord()
        self._get_redshift()
        self._get_duration()

    def go(self, client=None):
        """
        Launch the creation of the Universe of GRBs.
        If no client is passed, it is done serially.

        :param client: 
        :returns: 
        :rtype: 

        """

        if client is not None:

            futures = client.map(self._grb_wrapper, self._parameter_servers)
            res = client.gather(futures)

            del futures
            del res

        else:

            res = [self._grb_wrapper(ps, serial=True)
                   for ps in self._parameter_servers]

        self._is_processed = True

    def save(self, file_name):
        """

        Save the infomation from the simulation to 
        and HDF5 file

        :param file_name: 
        :returns: 
        :rtype: 

        """

        if self._is_processed:

            grb_save_files = [
                os.path.abspath(
                    os.path.join(self._save_path,
                                 f"{self._grb_base_name}_{i}_store.h5")
                )
                for i in range(self._n_grbs)
            ]

            # create a survey file to save all the information from the run

            survey = Survey(
                grb_save_files=grb_save_files, population_file=self._population_file
            )

            survey.write(file_name)

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
