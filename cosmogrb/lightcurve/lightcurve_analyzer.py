from collections import abc
from cosmogrb.lightcurve.light_curve_storage import LightCurveStorage

import coloredlogs, logging
import cosmogrb.utils.logging

logger = logging.getLogger("cosmogrb.lightcurve.lc_analyzer")


class LightCurveAnalyzer(object, metaclass=abc.ABCMeta):
    def __init__(self, lightcurve, instrument):

        assert isinstance(lightcurve, LightCurveStorage)

        assert (
            lightcurve.instrument == instrument
        ), f"The lightcurve was not created for {instrument} but for {lightcurve.instrument}"

        self._lightcurve = lightcurve

        self._is_detected = False

        if self._lightcurve.n_counts_source > 0:

            self._process_dead_time()

            self._compute_detection()

        else:

            logger.debug(f"lightcurve {lightcurve.name} has no source counts. SKIPPING")
            
    @abc.abstractmethod
    def _compute_detection(self):

        pass

    @abc.abstractmethod
    def _process_dead_time(self):
        pass

    @property
    def is_detected(self):
        return self._is_detected

    @abc.abstractmethod
    def dead_time_of_interval(self, tmax, tmin):

        pass

    def exposure_of_interval(self, tmin, tmax):
        """
        return the exposure of the interval


        :param tmin: 
        :param tmax: 
        :returns: 
        :rtype: 

        """

        return (tmax - tmin) - self.dead_time_per_interval(tmin, tmax)
