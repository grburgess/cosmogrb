import abc
from cosmogrb.lightcurve.light_curve_storage import LightCurveStorage


class LightCurveAnalyzer(object, metaclass=abc.ABCMeta):
    def __init__(self, lightcurve):

        assert isinstance(lightcurve, LightCurveStorage)

        self._lightcurve = lightcurve

        self._is_detected = False

        self._process_dead_time()

        self._compute_detection()

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
