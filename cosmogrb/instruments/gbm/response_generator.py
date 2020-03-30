import os
from gbm_drm_gen import DRMGenTTE
from cosmogrb.instruments.gbm.gbm_orbit import gbm_orbit
from cosmogrb.utils.package_utils import get_path_of_data_file
import coloredlogs, logging
import cosmogrb.utils.logging

# TODO: add occult to config
from cosmogrb import cosmogrb_config


logger = logging.getLogger("cosmogrb.gbm.response_gen")

_det_translate = dict(
    n0="NAI_00",
    n1="NAI_01",
    n2="NAI_02",
    n3="NAI_03",
    n4="NAI_04",
    n5="NAI_05",
    n6="NAI_06",
    n7="NAI_07",
    n8="NAI_08",
    n9="NAI_09",
    na="NAI_10",
    nb="NAI_11",
    b0="BGO_00",
    b1="BGO_01",
)


class ResponseGenerator(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:

            logger.debug("I'm creating a new instance! Should only happen once")

            cls._instance = super(ResponseGenerator, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(self):

        T0 = gbm_orbit.T0

        self._detectors = {}
        self._mc_energies = {}
        self._ebounds = {}
        
        logger.debug("creating response generators")

        for k, v in _det_translate.items():

            drm_gen = DRMGenTTE(
                det_name=_det_translate[k],
                time=1,
                T0=T0,
                cspecfile=get_path_of_data_file(
                    os.path.join("gbm_cspec", f"{k}.pha")
                ),
                poshist=get_path_of_data_file("posthist.fit"),
                mat_type=2,
                occult=False,
            )
            logger.debug(f"created {k} rsp gen")

            self._detectors[k] = drm_gen
            self._mc_energies[k] = drm_gen.monte_carlo_energies
            self._ebounds[k] = drm_gen.ebounds

    @property
    def detectors(self):
        return self._detectors

    @property
    def mc_energies(self):
        return self._mc_energies

    @property
    def ebounds(self):
        return self._ebounds
    
    

    def set_time(self, time, det_name):
        """
        set the time of the specific response generator

        :param time: 
        :param det_name: 
        :returns: 
        :rtype: 

        """

        assert det_name in self._detectors
        
        logger.debug(f"setting time of {det_name} to {time}")
        
        self._detectors[det_name].set_time(time)

    def set_location(self, ra, dec, det_name):
        """

        set the location of the specific reponse generator

        :param time: 
        :param det_name: 
        :returns: 
        :rtype: 

        """

        assert det_name in self._detectors

        logger.debug(f"setting location of {det_name} to {ra}, {dec}")
        
        self._detectors[det_name].set_location(ra, dec)

        return self._detectors[det_name].matrix.T
        
gbm_response_generator = ResponseGenerator()
