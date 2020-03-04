import matplotlib.pyplot as plt
import numpy as np


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

        self._pha = pha

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

            original_idx = np.logical_and(orginal_idx, idx_lo)

        if emax is not None:

            chan = self._ebounds.searchsorted(emax)

            idx_hi = pha < chan

            original_idx = np.logical_and(original_idx, idx_hi)

        return original_idx

    def display_lightcurve(self, dt=1, emin=None, emax=None, ax=None, **kwargs):

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        tmin = self._times.min()
        tmax = self._times.max()

        bins = np.arange(tmin, tmax, dt)

        idx = np.ones_like(self._times, dtype=bool)

        # filter channels if requested

        idx = self._select_channel(emin, emax, self._pha, idx)

        times = self._times[idx]

        ax.hist(times, bins=bins, histtype="step", lw=2, ec="k")

        return fig

    def display_background(self, dt=1, emin=None, emax=None, ax=None, **kwargs):

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        tmin = self._times.min()
        tmax = self._times.max()

        bins = np.arange(tmin, tmax, dt)

        idx = np.ones_like(self._times_background, dtype=bool)

        # filter channels if requested

        idx = self._select_channel(emin, emax, self._pha_background, idx)

        times = self._times_background[idx]

        ax.hist(times, bins=bins, histtype="step", lw=2, ec="r")

        return fig
