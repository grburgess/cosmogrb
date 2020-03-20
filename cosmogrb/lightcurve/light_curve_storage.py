import matplotlib.pyplot as plt
import numpy as np

from cosmogrb.utils.plotting import step_plot, channel_plot


class LightCurveStorage(object):
    def __init__(
        self,
        name,
        tstart,
        tstop,
        time_adjustment,
        pha,
        times,
        pha_source,
        times_source,
        pha_background,
        times_background,
        channels,
        ebounds,
        T0,
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

        self._name = name

        self._tstart = tstart
        self._tstop = tstop
        self._time_adjustment = time_adjustment

        self._pha = pha.astype(int)

        self._times = times

        self._pha_source = pha_source
        self._times_source = times_source

        self._pha_background = pha_background
        self._times_background = times_background

        self._channels = channels
        self._ebounds = ebounds

        self._T0 = T0

    @property
    def name(self):
        return self._name

    @property
    def tstart(self):
        return self._tstart

    @property
    def tstop(self):
        return self._tstop

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

    @property
    def time_adjustment(self):
        return self._time_adjustment

    def _select_channel(self, emin, emax, pha, original_idx):

        if emin is not None:

            chan = self._ebounds.searchsorted(emin)

            idx_lo = pha > chan

            original_idx = np.logical_and(original_idx, idx_lo)

        if emax is not None:

            chan = self._ebounds.searchsorted(emax)

            idx_hi = pha < chan

            original_idx = np.logical_and(original_idx, idx_hi)

        return original_idx

    def _select_time(self, tmin, tmax, times, original_idx):

        if tmin is not None:

            idx_lo = times > tmin

            original_idx = np.logical_and(original_idx, idx_lo)

        if tmax is not None:

            idx_hi = times < tmax

            original_idx = np.logical_and(original_idx, idx_hi)

        return original_idx

    def _prepare_lightcurve(self, dt, emin, emax, times, pha):

        tmin = times.min()
        tmax = times.max()

        bins = np.arange(tmin, tmax, dt)

        idx = np.ones_like(times, dtype=bool)

        # filter channels if requested

        idx = self._select_channel(emin, emax, pha, idx)

        times = times[idx]

        # histogram the counts and convert to a rate

        counts, edges = np.histogram(times, bins=bins)

        rate = counts / dt

        xbins = np.vstack([edges[:-1], edges[1:]]).T

        return xbins, rate

    def display_lightcurve(self, dt=1, emin=None, emax=None, ax=None, **kwargs):

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        xbins, rate = self._prepare_lightcurve(dt, emin, emax, self._times, self._pha)

        step_plot(xbins, rate, ax=ax, **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel("rate")

        return fig

    def display_background(self, dt=1, emin=None, emax=None, ax=None, **kwargs):

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        xbins, rate = self._prepare_lightcurve(
            dt, emin, emax, self._times_background, self._pha_background
        )

        step_plot(xbins, rate, ax=ax, **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel("rate")

        return fig

    def display_source(self, dt=1, emin=None, emax=None, ax=None, **kwargs):

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        xbins, rate = self._prepare_lightcurve(
            dt, emin, emax, self._times_source, self._pha_source
        )

        step_plot(xbins, rate, ax=ax, **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel("rate")

        return fig

    def _prepare_spectrum(self, tmin, tmax, times, pha):

        idx = np.ones_like(times, dtype=bool)

        # filter times

        idx = self._select_time(tmin, tmax, times, idx)

        # down select the pha

        pha = pha[idx]

        channels = np.append(self._channels, self._channels[-1] + 1)

        
        counts, _ = np.histogram(pha, bins = channels - 0.5)

        return counts

    def _compute_rates(self, threshold=5, background_accumulation_time=17, time_scale=1, emin=None, emax=None):

        pass

    
    def display_count_spectrum(self, tmin=None, tmax=None, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param tmin: 
        :param tmax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        emin = self._ebounds[:-1]
        emax = self._ebounds[1:]

        counts = self._prepare_spectrum(tmin, tmax, self._times, self._pha)

        # plot counts and background for the currently selected data

        channel_plot(ax, emin, emax, counts, **kwargs)

        return fig


    def display_count_spectrum_source(self, tmin=None, tmax=None, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param tmin: 
        :param tmax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        emin = self._ebounds[:-1]
        emax = self._ebounds[1:]

        counts = self._prepare_spectrum(tmin, tmax, self._times_source, self._pha_source)

        # plot counts and background for the currently selected data

        channel_plot(ax, emin, emax, counts, **kwargs)

        return fig

    def display_count_spectrum_background(self, tmin=None, tmax=None, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param tmin: 
        :param tmax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        emin = self._ebounds[:-1]
        emax = self._ebounds[1:]

        counts = self._prepare_spectrum(tmin, tmax, self._times_background, self._pha_background)

        # plot counts and background for the currently selected data

        channel_plot(ax, emin, emax, counts, **kwargs)

        
        return fig
