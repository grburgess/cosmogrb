import numpy as np

from cosmogrb.utils.plotting import step_plot


def channel_plot(ax, chan_min, chan_max, counts, **kwargs):
    """FIXME! briefly describe function

    :param ax:
    :param chan_min:
    :param chan_max:
    :param counts:
    :returns:
    :rtype:

    """

    chans = np.vstack([chan_min, chan_max]).T
    width = chan_max - chan_min

    step_plot(chans, counts / width, ax, **kwargs)
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel("Channel Energy")

    ax.set_ylabel("cnts/s/energy")
