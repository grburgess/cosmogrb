import numpy as np
from gbmgeometry import PositionInterpolator
from cosmogrb.utils.package_utils import get_path_of_data_file
import coloredlogs, logging
import cosmogrb.utils.logging


logger = logging.getLogger("cosmogrb.gbm.gbm_orbit")


class GBMOrbit(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:

            logger.debug("I'm creating a new instance! Should only happen once")

            cls._instance = super(GBMOrbit, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance


    def __init__(self):

        self._T0 = 576201540.940077

        logger.debug("Setting up the GBM orbit")
        
        self._interpolator = PositionInterpolator.from_posthist_hdf5(
            get_path_of_data_file("posthist.h5"), T0=self._T0
        )

        self._tmin, self._tmax = self._interpolator.minmax_time()

        self._delta_time = self._tmax - self._tmin

    @property
    def random_orbit_time(self):
        return np.random.uniform(self._tmin, self._tmax)
        
    @property
    def position_interpolator(self):
        return self._interpolator

    @property
    def T0(self):
        return self._T0

    @property
    def met(self, time):
        return self._interpolator.met(time)







gbm_orbit = GBMOrbit()
