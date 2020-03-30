from cosmogrb.io.grb_save import GRBSave
import collections

from cosmogrb.utils.plotting.skyplot import skyplot


class ReloadedUniverse(object):
    def __init__(self, *grb_saves):

        self._internal_storage = collections.OrderedDict()

        for grb in grb_saves:

            reloaded_grb = GRBSave.from_file(grb)

            self._internal_storage[reloaded_grb.name] = reloaded_grb

    @property
    def grb_names(self):
        return list(self._internal_storage.keys())

    def plot_grb_postions(
        self,
        ax=None,
        projection="astro degrees mollweide",
        center=None,
        radius=10,
        **kwargs
    ):

        ax = skyplot(ax=ax, projection=projection, center=center, radius=radius)

        ra = []
        dec = []

        for name, grb in self._internal_storage.items():

            ra.append(grb.ra)
            dec.append(grb.dec)
        
        ax.scatter(ra , dec,  s=40,transform=ax.get_transform("icrs"))

        return dec
        

    def __getitem__(self, key):

        if key in self._internal_storage:

            return self._internal_storage[key]

        else:

            raise ValueError(
                "Configuration key %s does not exist in %s." % (key, self._filename)
            )
