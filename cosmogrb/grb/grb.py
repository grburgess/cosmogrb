import h5py
import abc
import pandas as pd
from IPython.display import display

# import concurrent.futures as futures
import collections


from dask.distributed import worker_client

# from cosmogrb import cosmogrb_client

from cosmogrb.sampler.source import SourceFunction
from cosmogrb.utils.hdf5_utils import recursively_save_dict_contents_to_group
import coloredlogs, logging
import cosmogrb.utils.logging
from cosmogrb import cosmogrb_config


logger = logging.getLogger("cosmogrb.grb")


class SourceParameter(object):
    def __init__(self, default=None, vmin=None, vmax=None):

        self.name = None
        self._vmin = vmin
        self._vmax = vmax
        self._default = default

    @property
    def default(self):
        return self._default

    def __get__(self, obj, type=None) -> object:

        try:

            return obj._source_params[self.name]

        except:
            obj._source_params[self.name] = self._default

        return obj._source_params[self.name]

        return obj._source_params[self.name]

    def __set__(self, obj, value) -> None:
        self._is_set = True

        if self._vmin is not None:
            assert (
                value >= self._vmin
            ), f"trying to set {self.x} to a value below {self._vmin} is not allowed"

        if self._vmax is not None:
            assert (
                value <= self._vmax
            ), f"trying to set {self.name} to a value above {self._vmax} is not allowed"

        obj._source_params[self.name] = value


class GRBMeta(type):
    def __new__(mcls, name, bases, attrs, **kwargs):

        cls = super().__new__(mcls, name, bases, attrs, **kwargs)

        # Compute set of abstract method names
        abstracts = {
            name
            for name, value in attrs.items()
            if getattr(value, "__isabstractmethod__", False)
        }
        for base in bases:
            for name in getattr(base, "__abstractmethods__", set()):
                value = getattr(cls, name, None)
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name)
        cls.__abstractmethods__ = frozenset(abstracts)

        ### parameters

        for k, v in attrs.items():

            if isinstance(v, SourceParameter):
                v.name = k

        return cls

    def __subclasscheck__(cls, subclass):
        """Override for issubclass(subclass, cls)."""
        if not isinstance(subclass, type):
            raise TypeError("issubclass() arg 1 must be a class")
        # Check cache

        # Check the subclass hook
        ok = cls.__subclasshook__(subclass)
        if ok is not NotImplemented:
            assert isinstance(ok, bool)
            if ok:
                cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        # Check if it's a direct subclass
        if cls in getattr(subclass, "__mro__", ()):
            cls._abc_cache.add(subclass)
            return True
        # Check if it's a subclass of a registered class (recursive)
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True
        # Check if it's a subclass of a subclass (recursive)
        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        return False


class GRB(object, metaclass=GRBMeta):
    def __init__(
        self,
        name="SynthGRB",
        duration=1,
        z=1,
        T0=0,
        ra=0,
        dec=0,
        source_function_class=None,
        **kwargs,
    ):
        """
        A basic GRB

        :param name: 
        :param verbose: 
        :returns: 
        :rtype: 

        """
        self._source_params = {}
        
        self._name = name
        self._T0 = T0
        self._duration = duration
        self._z = z
        self._ra = ra
        self._dec = dec

        assert z > 0, f"z: {z} must be greater than zero"
        assert duration > 0, f"duration: {duration} must be greater than zero"

        logger.debug(f"created a GRB with name: {name}")
        logger.debug(f"created a GRB with ra: {ra} and dec: {dec}")
        logger.debug(f"created a GRB with redshift: {z}")
        logger.debug(f"created a GRB with duration: {duration} and T0: {T0}")

        # create an empty list for the light curves
        # eetc
        self._lightcurves = collections.OrderedDict()
        self._responses = collections.OrderedDict()
        self._backgrounds = collections.OrderedDict()

        assert issubclass(source_function_class, SourceFunction)
        self._source_function = source_function_class

        # now set any source parameters that were passed

        for k, v in kwargs.items():

            if k in self._source_params:

                self._source_params[k] = kwargs[k]

        # this stores extra information
        # about the GRB that can be used later
        self._extra_info = {}

        self._setup()

    @abc.abstractmethod
    def _setup(self):

        pass

    def _add_background(self, name, background):

        self._backgrounds[name] = background

    def _add_response(self, name, response):

        self._responses[name] = response

        logger.debug(f"Added response: {name}")

    def _add_lightcurve(self, lightcurve):
        """
        add a light curve to the GRB. This is really just adding 
        a detector on

        :param lightcurve: 
        :returns: 
        :rtype: 

        """

        self._lightcurves[lightcurve.name] = lightcurve

        logger.debug(f"Added lightcuve: {lightcurve.name}")

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

        list(self._lightcurves.values())[0].display_energy_dependent_light_curve(
            time=time, energy=energy, ax=ax, cmap=cmap, **kwargs
        )

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param time: 
        :param ax: 
        :rtype: 
        :returns: 

        """

        list(self._lightcurves.values())[0].display_energy_integrated_light_curve(
            time=time, ax=ax, **kwargs
        )

    def go(self, client=None, serial=False):

        if not serial:

            if client is not None:

                futures = client.map(process_lightcurve, self._lightcurves.values())

                results = client.gather(futures)

            else:

                with worker_client() as client:

                    futures = client.map(process_lightcurve, self._lightcurves.values())

                    results = client.gather(futures)

            del futures

        else:

            results = [process_lightcurve(lc) for lc in self._lightcurves.values()]

        for lc in results:

            #            lc = future.result()

            self._lightcurves[lc.name].set_storage(lc)

    def save(self, file_name, clean_up=False):
        """
        save the grb to an HDF5 file


        :param file_name: 
        :returns: 
        :rtype: 

        """

        with h5py.File(file_name, "w") as f:

            # save the general
            f.attrs["grb_name"] = self._name
            f.attrs["n_lightcurves"] = len(self._lightcurves)
            f.attrs["T0"] = self._T0
            f.attrs["z"] = self._z
            f.attrs["duration"] = self._duration
            f.attrs["ra"] = self._ra
            f.attrs["dec"] = self._dec

            # store the source function parameters

            recursively_save_dict_contents_to_group(f, "source", self._source_params)

            # now save everything from the detectors

            # store any extra info if there is
            # some.

            if self._extra_info:

                recursively_save_dict_contents_to_group(
                    f, "extra_info", self._extra_info
                )

            det_group = f.create_group("detectors")

            for _, lightcurve in self._lightcurves.items():

                lc = lightcurve.lightcurve_storage

                lc_group = det_group.create_group(f"{lc.name}")
                lc_group.attrs["tstart"] = lc.tstart
                lc_group.attrs["tstop"] = lc.tstop
                lc_group.attrs["time_adjustment"] = lc.time_adjustment
                lc_group.attrs["instrument"] = lc.instrument

                if lc.extra_info:
                    recursively_save_dict_contents_to_group(
                        f, f"{lc.name}/extra_info", lc.extra_info
                    )

                lc_group.create_dataset("channels", data=lc.channels)

                # now create groups for the total, source and bkg
                # counts

                total_group = lc_group.create_group("total_signal")

                total_group.create_dataset("pha", data=lc.pha, compression="lzf")
                total_group.create_dataset("times", data=lc.times, compression="lzf")

                source_group = lc_group.create_group("source_signal")

                source_group.create_dataset(
                    "pha", data=lc.pha_source, compression="lzf"
                )
                source_group.create_dataset(
                    "times", data=lc.times_source, compression="lzf"
                )

                source_group = lc_group.create_group("background_signal")

                source_group.create_dataset(
                    "pha", data=lc.pha_background, compression="lzf"
                )
                source_group.create_dataset(
                    "times", data=lc.times_background, compression="lzf"
                )

                rsp_group = lc_group.create_group("response")

                rsp_group.create_dataset(
                    "matrix", data=lightcurve.response.matrix, compression="lzf"
                )
                rsp_group.create_dataset(
                    "energy_edges",
                    data=lightcurve.response.energy_edges,
                    compression="lzf",
                )
                rsp_group.create_dataset(
                    "channel_edges",
                    data=lightcurve.response.channel_edges,
                    compression="lzf",
                )
                rsp_group.attrs["geometric_area"] = lightcurve.response.geometric_area

            if clean_up:

                self._lightcurves.clear()

    def __repr__(self):

        return self._output().to_string()

    def info(self):

        self._output(as_display=True)

    def _output(self, as_display=False):

        std_dict = collections.OrderedDict()

        std_dict["name"] = self._name
        std_dict["z"] = self._z
        std_dict["ra"] = self._ra
        std_dict["dec"] = self._dec
        std_dict["duration"] = self._duration
        std_dict["T0"] = self._T0

        if as_display:

            std_df = pd.Series(data=std_dict, index=std_dict.keys())

            display(std_df.to_frame())

            source_df = pd.Series(
                data=self._source_params, index=self._source_params.keys()
            )

            display(source_df.to_frame())

            if self._extra_info is not None:

                extra_df = pd.Series(
                    data=self._extra_info, index=self._extra_info.keys()
                )

                display(extra_df.to_frame())

        else:

            for k, v in self._source_params.items():
                std_dict[k] = v

            if self._extra_info is not None:
                for k, v in self._extra_info.items():
                    std_dict[k] = v

        return pd.Series(data=std_dict, index=std_dict.keys())


def process_lightcurve(lc):
    return lc.process()
