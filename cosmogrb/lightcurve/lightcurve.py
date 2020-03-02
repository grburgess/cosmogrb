import numpy as np
import coloredlogs, logging
import cosmogrb.utils.logging

logger = logging.getLogger("cosmogrb.lightcurve")


class LightCurve(object):
    def __init__(
        self, source, background, response, name="lightcurve", grb_name="SynthGRB",
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

    def _sample_source(self):
        """
        samples the source times and energies

        :returns: 
        :rtype: 

        """

        logger.debug(f"{self._grb_name} {self._name}: sampling photons")

        times = self._source.sample_times()

        logger.debug(f"{self._grb_name} {self._name}: has {len(times)} initial photons")

        photons = self._source.sample_photons(times)

        logger.debug(f"{self._grb_name} {self._name} sampling response")

        pha = self._source.sample_channel(photons, self._response)

        logger.debug(f"{self._grb_name} {self._name}: now has digitized it's events")

        self._photons = photons
        self._initial_source_light_curves = times
        self._initial_source_channels = pha

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

    def _combine(self):
        """
        combine the source and background photons

        :returns: 
        :rtype: 

        """

        self._times = np.append(
            self._initial_bkg_light_curves, self._initial_source_light_curves
        )
        self._pha = np.append(self._initial_bkg_channels, self._initial_source_channels)

        idx = self._times.argsort()

        self._times = self._times[idx]
        self._pha = self._pha[idx]

        # now sort the background and source times for fun

        idx = self._initial_bkg_light_curves.argsort()

        self._times_background = self._initial_bkg_light_curves[idx]
        self._pha_background = self._initial_bkg_channels[idx]

        idx = self._initial_source_light_curves.argsort()

        self._times_source = self._initial_source_light_curves[idx]
        self._pha_source = self._initial_source_channels[idx]

    def process(self):

        self._sample_source()
        self._sample_background()

        self._combine()

        logger.debug(f"{self._grb_name} {self._name}: now has {sum(self._pha)} counts")

        self._filter_deadtime()

        logger.debug(f"{self._grb_name} {self._name}: now has {sum(self._pha)} counts")

        # now create a lightcurve storage

        self._lc_storage = LightCurveStorage(
            pha=self._pha,
            times=self._times,
            pha_source=self._pha_source,
            times_source=self._times_source,
            pha_background=self._pha_background,
            times_background=self._times_background,
            channels=self._channels,
            ebounds=self._ebounds,
        )

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

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param time: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        self._source.display_energy_integrated_light_curve(time=time, ax=ax, **kwargs)

    @property
    def times(self):
        return self._times

    @property
    def pha(self):
        return self._pha

    @property
    def pha_source(self):
        return self._pha_source

    @property
    def times_source(self):
        return self._times_source

    @property
    def pha_background(self):
        return self._pha_background

    @property
    def times_background(self):
        return self._times_background

    def _filter_deadtime(self):

        pass

    @property
    def name(self):
        return self._name


class LightCurveStorage(object):
    def __init__(
        self,
        pha,
        times,
        pha_source,
        times_source,
        pha_background,
        times_background,
        channels,
        ebounds,
        T0=0,
    ):
        """
        Container class for light curve objects

        :param pha: 
        :param times: 
        :param pha_source: 
        :param times_source: 
        :param pha_background: 
        :param times_background: 
        :param channels: 
        :param ebounds: 
        :param T0: 
        :returns: 
        :rtype: 

        """

        self._pha = pha
        self._times = times + T0

        self._pha_source = pha_source
        self._times_source = times_source + T0

        self._pha_background = pha_background
        self._times_background = times_background + T0

        self._channels = channels
        self._ebounds = ebounds

        self._T0 = T0

    @property
    def T0(self):
        return self._T0

    @property
    def channels(self):
        return self._channels

    @property
    def ebounds(self):
        return self._ebounds

    @property
    def times(self):
        return self._times

    @property
    def pha(self):
        return self._pha

    @property
    def pha_source(self):
        return self._pha_source

    @property
    def times_source(self):
        return self._times_source

    @property
    def pha_background(self):
        return self._pha_background

    @property
    def times_background(self):
        return self._times_background
