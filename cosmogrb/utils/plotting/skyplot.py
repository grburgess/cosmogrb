from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt
from cosmogrb.utils.plotting.projections import *


def skyplot(ax = None, projection="astro degrees mollweide",center=None, radius=10.):

    if ax is None:

        assert projection in [
            "astro degrees aitoff",
            "astro degrees mollweide",
            "astro hours aitoff",
            "astro hours mollweide",
            "astro globe",
            "astro zoom",
        ]

        skw_dict = dict(projection=projection)

        if projection in ["astro globe", "astro zoom"]:

            if center is None:
                
                center = SkyCoord(0,0, unit='deg')

            skw_dict = dict(projection=projection, center=center)

        if projection == "astro zoom":

            assert radius is not None, "you must specify a radius"

            skw_dict = dict(projection=projection, center=center, radius=radius)

        fig, ax = plt.subplots(subplot_kw=skw_dict)

    else:

        fig = ax.get_figure()
        
    ax.grid()

    return ax
