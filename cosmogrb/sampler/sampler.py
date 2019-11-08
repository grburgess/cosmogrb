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
        
        self._tstart = tstart
        self._tstop = tstop

    def sample_times(self):

        raise NotImplementedError()

    def sample_channel(self, size=None):

        raise NotImplementedError()

    @property
    def tstart(self):
        return self._tstart

    @property
    def tstop(self):
        return self._tstop

    @property
    def times(self):
        return self._times
