import numba as nb
import numpy as np


from cosmogrb.lightcurve import LightCurveAnalyzer
from cosmogrb.utils.time_interval import TimeIntervalSet

import coloredlogs, logging
import cosmogrb.utils.logging
import dask

logger = logging.getLogger("cosmogrb.gbm.lc_analyzer")


_base_timescale = 0.016

_trigger_energy_ranges = {
    "a": (50.0, 300.0),
    "b": (25.0, 50.0),
    "c": (100.0, None),
    "d": (300.0, None),
}

_trigger_time_scales = {
    "a": [_base_timescale * (2 ** i) for i in range(10)],
    "b": [_base_timescale * (2 ** i) for i in range(10)],
    "c": [_base_timescale * (2 ** i) for i in range(9)],
    "d": [_base_timescale * (2 ** i) for i in range(4)],
}


class GBMLightCurveAnalyzer(LightCurveAnalyzer):
    """Documentation for GBMLightCurveAnalyzer

    """

    def __init__(
        self, lightcurve, threshold=4.5, background_duration=17, pre_window=4.0
    ):

        self._threshold = threshold
        self._background_duration = background_duration
        self._pre_window = pre_window

        self._base_timescale = _base_timescale
        self._trigger_time_scales = _trigger_time_scales
        self._trigger_energy_ranges = _trigger_energy_ranges

        self._n_bins_background = int(
            np.floor(self._background_duration / self._base_timescale)
        )
        self._n_bins_pre = int(np.floor(self._pre_window / self._base_timescale))

        self._detection_time = None
        self._detection_time_scale = None

        super(GBMLightCurveAnalyzer, self).__init__(lightcurve, instrument="GBM")

    def _compute_detection(self):

        # first we just need to compute the dead_time per intervals

        bins, counts = self._lightcurve.binned_counts(
            self._base_timescale, emin=None, emax=None, tmin=None, tmax=None
        )

        starts = bins[:, 0]
        stops = bins[:, 1]

        dead_time_per_interval = [self.dead_time_of_interval(x, y) for x, y in bins]

        #        self._dead_time_per_interval = dask.compute(*dead_time_per_interval)
        # go thru each energy range and look for a detection

        for k, (emin, emax) in self._trigger_energy_ranges.items():

            logger.debug(f"checking energy rage {emin}-{emax}")

            _, counts = self._lightcurve.binned_counts(
                self._base_timescale, emin, emax, tmin=None, tmax=None
            )

            # now build a time interval set

            ts = TimeIntervalSet.from_starts_and_stops(
                starts, stops, counts, dead_time_per_interval
            )

            # now check each of the GBM trigger time scales

            if sum(counts) == 0:

                # in this energy range we found no counts

                logger.debug("zero counts in light curve... skipping")

                continue

            for time_scale in self._trigger_time_scales[k]:

                logger.debug(f"checking time scale {time_scale}")

                n_bins_src = int(np.floor(time_scale / self._base_timescale))

                detected, time = _run_trigger(
                    self._n_bins_background,
                    self._n_bins_pre,
                    n_bins_src,
                    starts,
                    stops,
                    counts,
                    ts.exposures,
                    self._threshold,
                )

                # if there is a detection we can stop
                # because there is no need to search
                # for more

                if detected:

                    logger.debug(
                        f"found detection for energy range {emin}-{emax} at timescale {time_scale}"
                    )

                    self._is_detected = True
                    self._detection_time = time
                    self._detection_time_scale = time_scale

                    break

            # break out of the loop if we are done

            if self._is_detected:

                break

        # if we have not detected anything then we are done

        # if not self._is_detected:

        #     print("NO DETECTION")

    @property
    def detection_time_scale(self):
        return self._detection_time_scale

    @property
    def detection_time(self):
        return self._detection_time

    def _process_dead_time(self):

        dead_time_per_event = _calculate_dead_time_per_event(
            self._lightcurve.times, self._lightcurve.pha
        )

        self._dead_time_per_event = dead_time_per_event

    def dead_time_of_interval(self, tmin, tmax):
        """
        get the dead time over and interval


        :param tmin: 
        :param tmax: 
        :returns: 
        :rtype: 

        """

        # get the selection of counts for this interval
        idx = self._lightcurve.get_idx_over_interval(tmin, tmax)

        dead_time = self._dead_time_per_event[idx].sum()

        #        dead_time = _sum_dead_time(self._dead_time_per_event[idx], len(idx))

        return dead_time


@nb.njit(fastmath=True, parallel=False, cache=True, nogil=True)
def _sum_dead_time(dead_time_per_event, N):

    dead_time = 0.0
    for i in nb.prange(N):

        dead_time += dead_time_per_event[i]

    return dead_time


@nb.njit(fastmath=True, cache=False)
def _run_trigger(
    n_bins_background,
    n_bins_source,
    n_bins_pre,
    starts,
    stops,
    counts,
    exposure,
    threshold,
):

    for i in range(len(counts)):

        if i + n_bins_background + n_bins_pre + n_bins_source < len(stops):

            # bkg_exposure = starts[i + n_bins_background] - starts[i]
            bkg_exposure = exposure[i : i + n_bins_background].sum()

            background_counts = counts[i : i + n_bins_background].sum()

            # src

            src_idx = i + n_bins_background + n_bins_pre

            # src_exposure = starts[src_idx + n_bins_source] - starts[src_idx]
            src_exposure = exposure[src_idx : src_idx + n_bins_source].sum()

            src_counts = counts[src_idx : src_idx + n_bins_source].sum()

            sig = dumb_significance(
                src_counts, background_counts, src_exposure, bkg_exposure
            )

            # print(f"sig: {sig}")
            if (sig >= threshold) and (starts[src_idx] > 0.0):

                return True, starts[src_idx]

                # return sig, starts[src_idx + n_bins_source]

        else:

            return False, 0


@nb.njit(fastmath=True, cache=False)
def _calculate_dead_time_per_event(times, pha):
    """
    Computes an array of deadtimes following the perscription of Meegan et al. (2009).
    The array can be summed over to obtain the total dead time
    """
    dead_time_per_event = np.zeros_like(times)
    overflow_mask = pha == 127  # specific to gbm! should work for CTTE

    # From Meegan et al. (2009)
    # Dead time for overflow (note, overflow sometimes changes)
    dead_time_per_event[overflow_mask] = 10.0e-6  # s

    # Normal dead time
    dead_time_per_event[~overflow_mask] = 2.0e-6  # s

    return dead_time_per_event


@nb.njit(fastmath=True, cache=False)
def dumb_significance(Non, Noff, on_exposure, off_exposure):

    alpha = on_exposure / off_exposure

    Nb = alpha * Noff
    Ns = Non - Nb
    return Ns / np.sqrt(Nb)
