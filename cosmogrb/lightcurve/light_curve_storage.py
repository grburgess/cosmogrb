import pandas as pd
from IPython.display import display
import collections
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
        extra_info
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

        self._n_counts = self._times.shape[0]
        
        self._pha_source = pha_source
        self._times_source = times_source

        self._n_counts_source = self._times_source.shape[0]
        
        self._pha_background = pha_background
        self._times_background = times_background

        self._n_counts_background = self._times_background.shape[0]
        
        self._channels = channels
        self._ebounds = ebounds

        self._T0 = T0

        self._extra_info = extra_info
        
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
    def n_counts(self):
        return self._n_counts

    @property
    def n_counts_source(self):
        return self._n_counts_source

    @property
    def n_counts_background(self):
        return self._n_counts_background
    
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

    @property
    def extra_info(self):
        return self._extra_info

    
    def _select_channel(self, emin, emax, pha, original_idx=None):
        """
        return the idx of events between certain channels

        :param emin: 
        :param emax: 
        :param pha: 
        :param original_idx: 
        :returns: 
        :rtype: 

        """

        if original_idx is None:

            original_idx = np.ones_like(pha, dtype=bool)

        if emin is not None:

            chan = self._ebounds.searchsorted(emin)

            idx_lo = pha > chan

            original_idx = np.logical_and(original_idx, idx_lo)

        if emax is not None:

            chan = self._ebounds.searchsorted(emax)

            idx_hi = pha < chan

            original_idx = np.logical_and(original_idx, idx_hi)

        return original_idx

    def _select_time(self, tmin, tmax, times, original_idx=None):
        """
        return the idx of event between certain times

        :param tmin: 
        :param tmax: 
        :param times: 
        :param original_idx: 
        :returns: 
        :rtype: 

        """

        if original_idx is None:

            original_idx = np.ones_like(times, dtype=bool)

        if tmin is not None:

            idx_lo = times > tmin

            original_idx = np.logical_and(original_idx, idx_lo)

        if tmax is not None:

            idx_hi = times < tmax

            original_idx = np.logical_and(original_idx, idx_hi)

        return original_idx

    def get_idx_over_interval(self, tmin, tmax):
        """
        returns the selection over an interval of the 
        full light curve

        :param tmin: 
        :param tmax: 
        :returns: 
        :rtype: 

        """

        return self._select_time(tmin, tmax, self._times)

    def _bin_lightcurve(self, dt, emin, emax, times, pha, tmin=None, tmax=None):
        """
        
        bin the light curve for plotting

        :param dt: 
        :param emin: 
        :param emax: 
        :param times: 
        :param pha: 
        :param tmin: 
        :param tmax: 
        :returns: 
        :rtype: 

        """

        if tmin is None:
            tmin = times.min()

        if tmax is None:
            tmax = times.max()

        assert (
            tmin < tmax
        ), f"the specified tmin and tmax are out of order ({tmin} > {tmax})"

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

    def binned_counts(self, dt, emin, emax, tmin=None, tmax=None):
        """

        get the time bins and counts for a given selection

        :param dt: 
        :param emin: 
        :param emax: 
        :param times: 
        :param pha: 
        :param tmin: 
        :param tmax: 
        :returns: 
        :rtype: 

        """

        bins, rate = self._bin_lightcurve(
            dt, emin, emax, self._times, self._pha, tmin, tmax
        )

        counts = (rate * dt).astype(int)

        return bins, counts

    def _display_lightcurve(
        self,
        times,
        pha,
        dt=1,
        tmin=None,
        tmax=None,
        emin=None,
        emax=None,
        ax=None,
        **kwargs,
    ):

        if ax is None:

            fig, ax = plt.subplots()

        else:

            fig = ax.get_figure()

        # do not try to plot one photon

        if len(times) <= 1:

            #            logging.warn('there were no')
            return fig

        xbins, rate = self._bin_lightcurve(
            dt=dt, emin=emin, emax=emax, times=times, pha=pha, tmin=tmin, tmax=tmax
        )

        step_plot(xbins, rate, ax=ax, **kwargs)

        ax.set_xlabel("time")
        ax.set_ylabel("rate")

        return fig

    def display_lightcurve(
        self, dt=1, tmin=None, tmax=None, emin=None, emax=None, ax=None, **kwargs
    ):
        """FIXME! briefly describe function

        :param dt: 
        :param tmin: 
        :param tmax: 
        :param emin: 
        :param emax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        fig = self._display_lightcurve(
            times=self._times,
            pha=self._pha,
            dt=dt,
            tmin=tmin,
            tmax=tmax,
            emin=emin,
            emax=emax,
            ax=ax,
            **kwargs,
        )

        return fig

    def display_background(
        self, dt=1, tmin=None, tmax=None, emin=None, emax=None, ax=None, **kwargs
    ):
        """
        display the background light curve

        :param dt: 
        :param tmin: 
        :param tmax: 
        :param emin: 
        :param emax: 
        :param ax: 
        :returns: 
        :rtype: 

        """
        fig = self._display_lightcurve(
            times=self._times_background,
            pha=self._pha_background,
            dt=dt,
            tmin=tmin,
            tmax=tmax,
            emin=emin,
            emax=emax,
            ax=ax,
            **kwargs,
        )

        return fig

    def display_source(
        self, dt=1, tmin=None, tmax=None, emin=None, emax=None, ax=None, **kwargs
    ):
        """
        display the source only light curve

        :param dt: 
        :param tmin: 
        :param tmax: 
        :param emin: 
        :param emax: 
        :param ax: 
        :returns: 
        :rtype: 

        """
        fig = self._display_lightcurve(
            times=self._times_source,
            pha=self._pha_source,
            dt=dt,
            tmin=tmin,
            tmax=tmax,
            emin=emin,
            emax=emax,
            ax=ax,
            **kwargs,
        )

        return fig

    def _bin_spectrum(self, tmin, tmax, times, pha):
        """
        bin the spectrum into counts

        :param tmin: 
        :param tmax: 
        :param times: 
        :param pha: 
        :returns: 
        :rtype: 

        """

        idx = np.ones_like(times, dtype=bool)

        # filter times

        idx = self._select_time(tmin, tmax, times, idx)

        # down select the pha

        pha = pha[idx]

        channels = np.append(self._channels, self._channels[-1] + 1)

        counts, _ = np.histogram(pha, bins=channels - 0.5)

        return counts

    def _display_count_spectrum(
        self, times, pha, tmin=None, tmax=None, ax=None, **kwargs
    ):
        """

        generic count spectrum plotter

        :param times: 
        :param pha: 
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

        counts = self._bin_spectrum(tmin, tmax, times, pha)

        # plot counts and background for the currently selected data

        channel_plot(ax, emin, emax, counts, **kwargs)

        return fig

    def display_count_spectrum(self, tmin=None, tmax=None, ax=None, **kwargs):
        """
        display the total count spectrum

        :param tmin: 
        :param tmax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        fig = self._display_count_spectrum(
            self._times, self._pha, tmin, tmax, ax, **kwargs
        )

        return fig

    def display_count_spectrum_source(self, tmin=None, tmax=None, ax=None, **kwargs):
        """
        display the source count spectrum

        :param tmin: 
        :param tmax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        fig = self._display_count_spectrum(
            self._times_source, self._pha_source, tmin, tmax, ax, **kwargs
        )

        return fig

    def display_count_spectrum_background(
        self, tmin=None, tmax=None, ax=None, **kwargs
    ):
        """
        display the background count spectrum

        :param tmin: 
        :param tmax: 
        :param ax: 
        :returns: 
        :rtype: 

        """

        fig = self._display_count_spectrum(
            self._times_background, self._pha_background, tmin, tmax, ax, **kwargs
        )

        return fig
    def __repr__(self):

        return self._output().to_string()

    def info(self):

        self._output(as_display=True)

    def _output(self, as_display=False):

        std_dict = collections.OrderedDict()

        std_dict["name"] = self._name
        std_dict["tstart"] = self._tstart
        std_dict["tstop"] = self._tstop
        std_dict["time adjustment"] = self._time_adjustment
        std_dict["T0"] = self._T0
        std_dict["n_counts"] = self._n_counts
        std_dict["n_counts_source"] = self._n_counts_source
        std_dict["n_counts_background"] = self._n_counts_background

        if as_display:

            std_df = pd.Series(data=std_dict, index=std_dict.keys())

            display(std_df.to_frame())

            if self._extra_info:

                extra_df = pd.Series(
                    data=self._extra_info, index=self._extra_info.keys()
                )

                display(extra_df.to_frame())

        else:

            if self._extra_info:
                for k, v in self._extra_info.items():
                    std_dict[k] = v

        return pd.Series(data=std_dict, index=std_dict.keys())
