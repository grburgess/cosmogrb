import numpy as np

from cosmogrb.instruments.gbm.gbm_lightcurve_analyzer import GBMLightCurveAnalyzer
from cosmogrb.grb.grb_detector import GRBDetector

import coloredlogs, logging
import cosmogrb.utils.logging

logger = logging.getLogger("cosmogrb.gbm.trigger")


class GBMTrigger(GRBDetector):
    def __init__(
        self, grb_save_file_name, threshold=4.5, simul_trigger_window=0.5, max_n_dets=12
    ):
        """

        Run the GBM trigger and the specified GRB. The will first order the GBM detectors
        by their angular distance to the GRB and then run through each to check for a detection
        in one of the GBM energy ranges and time scales. If a detection is found, a second detector with 
        detection is searched for requiring that its trigger exist in a window +/- the width specified

        :param grb_save_file_name: the file to run the trigger on
        :param threshold: the trigger threshold to use
        :param simul_trigger_window: the +/- window for simultaneous triggers
        :param max_n_dets: the maximum number of detectors to test
        :returns: 
        :rtype: 

        """

        super(GBMTrigger, self).__init__(grb_save_file_name)

        self._threshold = threshold
        self._simul_trigger_window = simul_trigger_window
        self._max_n_dets = max_n_dets

        self._triggered_times = []
        self._triggered_detectors = []
        self._triggered_time_scales = []

        # sort the detectors by their distance to the
        # grb
        self._setup_order_by_distance()

    def _setup_order_by_distance(self):

        # now we will go through the lightcurves
        # collect

        logger.debug(f"{self._grb_save.name} is having its detectors ordered ")

        angular_distances = []
        lc_names = []

        for name in self._grb_save.keys:

            if name.startswith("n"):

                lc = self._grb_save[name]["lightcurve"]
                lc_names.append(name)

                angular_distances.append(lc.extra_info["angle"])

                logger.debug(f"adding {name} with and {lc.extra_info['angle']}")

        angular_distances = np.array(angular_distances)
        lc_names = np.array(lc_names)

        # now attach the lc_names sorted by
        # the detector distance to the GRB

        idx = angular_distances.argsort()
        self._lc_names = lc_names[idx]

    @property
    def triggered_detectors(self):
        return self._triggered_detectors

    @property
    def triggered_times(self):
        return self._triggered_times

    @property
    def triggered_time_scales(self):
        return self._triggered_time_scales

    def _check_simultaneous_triggers(self, time):

        # go thru all the other trigger times and see
        # if this one is within the window of others

        detected = False

        for other_time in self._triggered_times:

            if (time >= (other_time - self._simul_trigger_window)) and (
                time <= (other_time + self._simul_trigger_window)
            ):
                # we found one!

                detected = True

                break
        # nothing close

        return detected

    def process(self):
        """
        Process the GBM detectors to find
        two simultaneous triggers

        :returns: 
        :rtype: 

        """

        n_triggered = 0

        n_tested = 0

        while (
            (n_tested < len(self._lc_names))
            and (not self._is_detected)
            and (n_tested < self._max_n_dets)
        ):

            lc = self._grb_save[self._lc_names[n_tested]]["lightcurve"]

            lc_analyzer = GBMLightCurveAnalyzer(
                lightcurve=lc, threshold=self._threshold
            )

            if lc_analyzer.is_detected:

                logger.debug(f"{self._lc_names[n_tested]} triggered!")
                # we saw something!
                # add the name and the time

                if n_triggered != 0:

                    # check the other trigger times to
                    # see if they are close to this one

                    if self._check_simultaneous_triggers(lc_analyzer.detection_time):

                        # ok, we found at least two triggers nearly the same time

                        self._is_detected = True
                        logger.debug(
                            f"{self._lc_names[n_tested]} is simultaneous with another detector"
                        )

                self._triggered_detectors.append(self._lc_names[n_tested])
                self._triggered_times.append(lc_analyzer.detection_time)
                self._triggered_time_scales.append(lc_analyzer.detection_time_scale)

                n_triggered += 1

            n_tested += 1

        self._extra_info['triggered_detectors'] = self._triggered_detectors
        self._extra_info['triggered_times'] = self._triggered_times
        self._extra_info['triggered_time_scales'] = self._triggered_time_scales
        
