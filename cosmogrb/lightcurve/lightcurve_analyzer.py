import abc
from cosmogrb.lightcurve.light_curve_storage import LightCurveStorage

class LightCurveAnalyzer(object, metaclass=abc.ABCMeta):
    def __init__(self, lightcurve):

        assert isinstance(lightcurve, LightCurveStorage)

    
        
        self._is_detected = False

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
    def dead_time_per_interval(self):

        pass
