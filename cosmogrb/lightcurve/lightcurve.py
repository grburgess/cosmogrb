import numpy as np

from cosmogrb.lightcurve.light_curve_storage import LightCurveStorage
from cosmogrb.utils.logging import setup_logger

logger = setup_logger(__name__)


class LightCurve(object):
    def __init__(
        self,
        name,
        source,
        background,
        response,
        instrument,
        T0=0,
        grb_name="SynthGRB",
        tstart=0,
        tstop=100.0,
    ):
        """
        Lightcurve generator f{lenource and backgroun after dead time filteringd
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

        self._tstart = tstart
        self._tstop = tstop

        assert tstop > tstart

        self._time_adjustment = 0

        # now set the response

        #        self._source.set_response(self._response)

        self._initial_source_light_curves = None
        self._initial_bkg_light_curves = None

        self._initial_source_channels = None
        self._initial_bkg_channels = None
        self._name = name
        self._grb_name = grb_name
        self._T0 = T0

        self._instrument = instrument

        # for holding information (numbers/str)
        # for special types

        self._extra_info = {}

    def set_time_adjustment(self, t):
        self._time_adjustment = t

    def _sample_source(self):
        """
        samples the source times and energies

        :returns:
        :rtype:

        """

        logger.debug(f"{self._grb_name} {self._name}: sampling source")

        times = self._source.sample_times()

        logger.debug(
            f"{self._grb_name} {self._name}: has {len(times)} initial source photons"
        )

        photons = self._source.sample_photons(times)

        logger.debug(f"{self._grb_name} {self._name} sampling response")

        pha = self._source.sample_channel(photons, self._response)

        logger.debug(
            f"{self._grb_name} {self._name}: now has digitized its events"
        )

        self._photons = photons
        self._initial_source_light_curves = times
        self._initial_source_channels = pha

        idx = self._initial_source_light_curves.argsort()

        self._times_source = self._initial_source_light_curves[idx]
        self._pha_source = self._initial_source_channels[idx]

    def _sample_background(self):
        """
        sample the background

        :returns:
        :rtype:

        """

        logger.debug(f"{self._grb_name} {self._name}: sampling background")

        self._initial_bkg_light_curves = self._background.sample_times()
        self._initial_bkg_channels = self._background.sample_channel(
            size=len(self._initial_bkg_light_curves)
        )

        idx = self._initial_bkg_light_curves.argsort()

        self._times_background = self._initial_bkg_light_curves[idx]
        self._pha_background = self._initial_bkg_channels[idx]

    def _combine(self):
        """
        combine the source and background photons

        :returns:
        :rtype:

        """

        self._times = np.append(
            self._initial_bkg_light_curves, self._initial_source_light_curves
        )

        self._pha = np.append(
            self._initial_bkg_channels, self._initial_source_channels
        )

        idx = self._times.argsort()

        self._times = self._times[idx]
        self._pha = self._pha[idx]

        logger.debug(
            f"{self._grb_name} {self._name} has {len(self._pha)} counts after combining "
        )

        # now sort the background and source times for fun

        # logging.debug(
        #     f"{self._grb_name} {self._name} has {len(self._pha_background)}  background counts after combining "
        # )

        # logging.debug(
        #     f"{self._grb_name} {self._name} has {len(self._pha_source)}  source counts after combining "
        # )

    def process(self):

        self._sample_source()
        self._sample_background()

        self._combine()

        self._filter_deadtime()

        logger.debug(
            f"{self._grb_name} {self._name}: now has {len(self._pha)} counts after dead time filtering"
        )

        # now create a lightcurve storage

        lc_storage = LightCurveStorage(
            name=self._name,
            tstart=self._tstart,
            tstop=self._tstop,
            time_adjustment=self._time_adjustment,
            pha=self._pha,
            times=self._times,
            pha_source=self._pha_source,
            times_source=self._times_source,
            pha_background=self._pha_background,
            times_background=self._times_background,
            channels=self._response.channels,
            ebounds=self._response.channel_edges,
            T0=self._T0,
            instrument=self._instrument,
            extra_info=self._extra_info,
        )

        return lc_storage

    def set_storage(self, lc_storage):
        self._lc_storage = lc_storage

    def display_energy_dependent_light_curve(
        self, time, energy, ax=None, cmap="viridis", **kwargs
    ):
        """FIXME! briefly describe function

        :param time:
        :param energy:
        :param ax:
        :param cmap:
        :returns:
        :rtype:

        """

        self._source.display_energy_dependent_light_curve(
            time=time, energy=energy, ax=ax, cmap=cmap, **kwargs
        )

    def display_time_dependent_spectrum(
        self, time, energy, ax=None, cmap="viridis", **kwargs
    ):
        """FIXME! briefly describe function

        :param time:
        :param energy:
        :param ax:
        :param cmap:
        :returns:
        :rtype:

        """

        self._source.display_time_dependent_spectrum(
            time=time, energy=energy, ax=ax, cmap=cmap, **kwargs
        )

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param time:
        :param ax:
        :returns:
        :rtype:

        """

        self._source.display_energy_integrated_light_curve(
            time=time, ax=ax, **kwargs
        )

    @property
    def time_adjustment(self):
        return self._lc_storage.time_adjustment

    @property
    def times(self):
        return self._lc_storage.times

    @property
    def pha(self):
        return self._lc_storage.pha

    @property
    def pha_source(self):
        return self._lc_storage.pha_source

    @property
    def times_source(self):
        return self._lc_storage.times_source

    @property
    def pha_background(self):
        return self._lc_storage.pha_background

    @property
    def times_background(self):
        return self._lc_storage.times_background

    def _filter_deadtime(self):

        pass

    @property
    def name(self):
        return self._name

    @property
    def response(self):
        return self._response

    @property
    def extra_info(self):
        return self._extra_info

    @property
    def lightcurve_storage(self):
        return self._lc_storage
