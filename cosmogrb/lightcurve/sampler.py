import numpy as np


class Sampler(object):

    def __init__(self, tstart, tstop):
        """
        Superclass of the background and source
        samplers

        :param tstart: 
        :param tstop: 
        :returns: 
        :rtype: 

        """


        # construct the times
        
        self._times = self._sample_times()


    def _filter_deadtime(self):

        pass

    
    def _sample_times(self):

        raise NotImplementedError()
        
    @property
    def times(self):
        return self._times
