import numpy as np
from numba import jit, njit



@jit
def background_poisson_generator(tstart, tstop, rate):
    """

    :param tstart: 
    :param tstop: 
    :param rate: 
    :returns: 
    :rtype: 

    """
    
    fmax = rate

    time = tstart

    arrival_times = [tstart]

    while time < tstop:

        time = time - (1.0 / fmax) * np.log(np.random.rand())
        test = np.random.rand()

        p_test = (intercept + slope * time) / fmax

        if test <= p_test:
            arrival_times.append(time)

    return np.array(arrival_times)



class BackgroundSpectrumTemplate(object):

    def __init__(self, counts):
        """
        A background template stores and samples 
        from a predefined background distribution

        :param counts: 
        :returns: 
        :rtype: 

        """


        self._counts = counts
        self._channels = np.range(len(counts))

        
        self._normalize_counts()

    def _normalize_counts(self):
        """
        get weights by normalizing the counts

        :returns: 
        :rtype: 

        """
        
        self._weights = self._counts / self._counts.sum()

    def sample_channel(self, size=None):
        """
        Sample from the background template

        :param size: 
        :returns: 
        :rtype: 

        """
        

        
        # sample a channel from the background
        return np.random.choice(self._channels,size=size, p=self._weights)
        

        


    @classmethod
    def from_file(cls, file_name):

        return cls()





class Background(object):

    def __init__(self, tstart, tstop, average_rate, background_spectrum_template):

        self._tstart = tstart
        self._tstop = tstop
        

    def _get_background_template(self):

        pass

    
class GBMBackground(Background):

    def __init__(self):

        
        

