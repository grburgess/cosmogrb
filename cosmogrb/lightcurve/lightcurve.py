import numpy as np


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

        pha = self._source.sample_channel(photons, self._response)

        if self._verbose:

            print(f"{self._grb_name} {self._name}: now has digitized it's events")

        self._photons = photons
        self._initial_source_light_curves = times
        self._initial_source_channels = pha

    def _sample_background(self):

        if self._verbose:

            print(f"{self._grb_name} {self._name}: sampling background")

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

    def _filter_deadtime(self):

        pass

    @property
    def name(self):
        return self._name
