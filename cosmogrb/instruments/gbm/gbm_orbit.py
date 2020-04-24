import numpy as np
from gbmgeometry import PositionInterpolator
from cosmogrb.utils.package_utils import get_path_of_data_file

from cosmogrb import cosmogrb_config

import coloredlogs, logging
import cosmogrb.utils.logging


logger = logging.getLogger("cosmogrb.gbm.gbm_orbit")


class GBMOrbit(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:

            logger.debug("i'm creating a new instance! should only happen once")

            cls._instance = super(GBMOrbit, cls).__new__(cls)
            # put any initialization here.
        return cls._instance

    def __init__(self):

        self._minimum_met = 576201540.940077
        self._maximum_time = 86519.99999904633
        self._T0 = self._minimum_met
        self._used_times = []

        logger.debug("Setting up the GBM orbit")

        self._interpolator = PositionInterpolator.from_poshist_hdf5(
            get_path_of_data_file("posthist.h5"), T0=self._T0
        )

        self._tmin, self._tmax = self._interpolator.minmax_time()

        self._delta_time = self._tmax - self._tmin

    @property
    def position_interpolator(self):
        return self._interpolator

    @property
    def T0(self):
        """
        The start of the MET for the posthist
        """
        return self._T0

    @property
    def random_time(self):

        time = np.random.uniform(0, self._maximum_time)
        self._used_times.append(time)

        return time

    def met(self, time):
        """
        Get the MET of the time relative time

        :param time: 
        :returns: 
        :rtype: 

        """

        return self._interpolator.met(time)


gbm_orbit = GBMOrbit()
