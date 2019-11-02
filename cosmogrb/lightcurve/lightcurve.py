import numpy as np
import numba as nb


class LightCurve(object):

    def __init__(self, source, background):

        self._source = source
        self._background = background

    def _filter_deadtime(self):

        pass


class GBMLightCurve(LightCurve):


    def __init__(self):


        
        super(GBMLightCurve, self).__init__(source=source,
                                            background=background)

    def _filter_deadtime(self):


        n_intervals = len(self._all_times)
        

@nb.njit
def _gbm_dead_time( time, pha, n_intervals):

    dead_time = 2.6e-6
    overflow_dead_Time = 10.6e-6
    par_dead_time = 0.5e-6
    
    filtered_time = np.zeros(n_intervals) - 9999
    filtered_pha = np.zeros(n_intervals) - 9999
    
    filtered_time[0] = time[0]
    filtered_pha[0] = pha[0]

    if pha[0] == 127:

        t_end = time[0] + overflow_dead_Time

    else:

        t_end = time[0] + dead_time

    t_end_par = time[0] + par_dead_time
        
    
    for i in range(1, n_intervals):

        if time[i] > t_end:
            filtered_time[i] = time[i]
            filtered_pha[i] = pha[i]

            if pha[i] == 127:

                t_end = time[i] + overflow_dead_Time
        
        
        

    
