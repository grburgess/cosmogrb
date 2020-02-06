import numpy as np
import numba as nb
from collections import OrderedDict

import copy

from cosmogrb.utils.tte_file import TTEFile


class LightCurve(object):
    def __init__(
        self,
        source,
        background,
        response,
        name="lightcurve",
        grb_name="SynthGRB",
        verbose=False,
    ):
        """
        Lightcurve generator for source and background
        per detector. 



        :param source: 
        :param background: 
        :returns: 
        :rtype: 

        """

        # # we want to make a deep copy because we will
        # # add the response in and we want it to be independent
        # self._source = copy.deepcopy(source)

        self._source = source

        self._background = background
        self._response = response

        # now set the response

#        self._source.set_response(self._response)
        
        self._initial_source_light_curves = None
        self._initial_bkg_light_curves = None

        self._initial_source_channels = None
        self._initial_bkg_channels = None
        self._name = name
        self._grb_name = grb_name

        self._verbose = verbose

    def _sample_source(self):

        if self._verbose:

            print(f"{self._grb_name} {self._name}: sampling photons")

        times = self._source.sample_times()

        if self._verbose:

            print(f"{self._grb_name} {self._name}: has {len(times)} initial photons")

        photons = self._source.sample_photons(times)

        if self._verbose:

            print(f"{self._grb_name} {self._name} sampling response")

        pha, selection = self._source.sample_channel(photons, self._response)

        if self._verbose:

            print(f"{self._grb_name} {self._name}: now has {sum(selection)} counts")

        selection = np.array(selection, dtype=bool)

        self._photons = photons

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

        if self._verbose:

            print(f"{self._grb_name} {self._name}: now has {sum(self._pha)} counts")

        self._filter_deadtime()

        if self._verbose:

            print(f"{self._grb_name} {self._name}: now has {sum(self._pha)} counts")

    @property
    def times(self):
        return self._times

    @property
    def pha(self):
        return self._pha

    def _filter_deadtime(self):

        pass


class GBMLightCurve(LightCurve):
    def __init__(self, source, background, response, name, grb_name, verbose=False):
        """FIXME! briefly describe function

        :param source: 
        :param background: 
        :param response: 
        :param name: 
        :param grb_name: 
        :param verbose: 
        :returns: 
        :rtype: 

        """

        super(GBMLightCurve, self).__init__(
            source=source,
            background=background,
            response=response,
            name=name,
            grb_name=grb_name,
            verbose=verbose,
        )

    def _filter_deadtime(self):

        n_intervals = len(self._times)
        time, pha, selection = _gbm_dead_time(self._times, self._pha, n_intervals)

        selection = np.array(selection, dtype=bool)

        if self._verbose:

            print(
                f"{self._grb_name} {self._name}: now has {sum(selection)} from {len(selection)} counts"
            )

        self._times = time[selection]
        self._pha = pha[selection]

    def write_tte(self):

        tstart = self._background.tstart + self._response.T0
        tstop = self._background.tstop + self._response.T0

        tte_file = TTEFile(
            det_name=self._response.detector_name,
            tstart=tstart,
            tstop=tstop,
            trigger_time=self._response.trigger_time,
            ra=self._response.ra,
            dec=self._response.dec,
            channel=np.arange(0, 128, dtype=np.int16),
            emin=self._response.channel_edges[:-1],
            emax=self._response.channel_edges[1:],
            pha=self._pha.astype(np.int16),
            time=self._times + self._response.T0,
        )

        tte_file.writeto(f"{self._grb_name}_{self._name}.fits", overwrite=True)


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
