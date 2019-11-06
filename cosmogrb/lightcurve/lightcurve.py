import numpy as np
import numba as nb
from collections import OrderedDict


from cosmogrb.lightcurve.tte import TTEFile


class LightCurve(object):
    def __init__(self, source, background, response):
        """
        Lightcurve generator for source and background
        per detector. 



        :param source: 
        :param background: 
        :returns: 
        :rtype: 

        """

        self._source = source
        self._background = background
        self._response = response

        self._initial_source_light_curves = None
        self._initial_bkg_light_curves = None

        self._initial_source_channels = None
        self._initial_bkg_channels = None

    def _sample_source(self):

        times = self._source.sample_times()

        photons = self._source.sample_photons(times)

        pha, selection = self._source.sample_channel(photons, self._response)

        selection = np.array(selection, dtype=bool)

        # we have to remove the photons that were not detected
        #

        self._initial_source_light_curves = times[selection]
        self._initial_source_channels = pha[selection]

    def _sample_background(self):

        self._initial_bkg_light_curves = self._background.sample_times()
        self._initial_bkg_channels = self._background.sample_channel(
            size=len(self._initial_bkg_light_curves)
        )

    def _combine(self):

        self._times = np.append(
            self._initial_bkg_light_curves, self._initial_source_light_curves
        )
        self._pha = np.append(self._initial_bkg_channels, self._initial_source_channels)

        idx = self._times.argsort()

        self._times = self._times[idx]
        self._pha = self._pha[idx]

    def process(self):

        self._sample_source()
        self._sample_background()
        self._combine()
        self._filter_deadtime()

    @property
    def times(self):
        return self._times

    @property
    def pha(self):
        return self._pha

    def _filter_deadtime(self):

        pass


class GBMLightCurve(LightCurve):
    def __init__(self, source, background, response):

        super(GBMLightCurve, self).__init__(
            source=source, background=background, response=response
        )

    def _filter_deadtime(self):

        n_intervals = len(self._times)
        time, pha, selection = _gbm_dead_time(self._times, self._pha, n_intervals)

        selection = np.array(selection, dtype=bool)

        self._times = time[selection]
        self._pha = pha[selection]

    def write_tte(self, file_name):

        tstart = self._background.tstart + self._response.T0
        tstop = self._background.tstop + self._response.T0

        tte_file = TTEFile(
            det_name=self._response.detector_name,
            tstart=tstart,
            tstop=tstop,
            trigger_time=self._response.trigger_time,
            ra=self._response.ra,
            dec=self._response.dec,
            channel=np.arange(1, 129, dtype=np.int16),
            emin=self._response.channel_edges[:-1],
            emax=self._response.channel_edges[1:],
            pha=self._pha,
            time=self._times,
        )


@nb.njit(fastmath=True)
def _gbm_dead_time(time, pha, n_intervals):

    dead_time = 2.6e-6
    overflow_dead_Time = 10.6e-6
    par_dead_time = 0.5e-6

    filtered_time = np.zeros(n_intervals)
    filtered_pha = np.zeros(n_intervals)
    selection = np.zeros(n_intervals)

    filtered_time[0] = time[0]
    filtered_pha[0] = pha[0]
    selection[0] = True

    if pha[0] == 127:

        t_end = time[0] + overflow_dead_Time

    else:

        t_end = time[0] + dead_time

    t_end_par = time[0] + par_dead_time

    for i in range(1, n_intervals):

        if time[i] > t_end:
            filtered_time[i] = time[i]
            filtered_pha[i] = pha[i]
            selection[i] = True
            if pha[i] == 127:

                t_end = time[i] + overflow_dead_Time

    return filtered_time, filtered_pha, selection
