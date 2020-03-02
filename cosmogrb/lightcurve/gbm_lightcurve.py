import numba as nb
import numpy as np

from cosmogrb.lightcurve.lightcurve import LightCurve
from cosmogrb.utils.tte_file import TTEFile

import coloredlogs, logging
import cosmogrb.utils.logging

logger = logging.getLogger("cosmogrb.lightcurve.gbm_lighcurve")


class GBMLightCurve(LightCurve):
    def __init__(self, source, background, response, name, grb_name):
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
        )

    def _filter_deadtime(self):

        n_intervals = len(self._times)
        time, pha, selection = _gbm_dead_time(self._times, self._pha, n_intervals)

        selection = np.array(selection, dtype=bool)

        logger.debug(
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
