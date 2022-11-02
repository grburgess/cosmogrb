import abc

# import concurrent.futures as futures
import collections
import logging

import h5py
import pandas as pd
from dask.distributed import worker_client
from IPython.display import display

from cosmogrb import cosmogrb_config
from cosmogrb.sampler.source_function import SourceFunction
from cosmogrb.utils.hdf5_utils import recursively_save_dict_contents_to_group
from cosmogrb.utils.logging import setup_logger
from cosmogrb.utils.meta import GRBMeta, RequiredParameter

# from cosmogrb import cosmogrb_client


logger = setup_logger(__name__)


class GRB(object, metaclass=GRBMeta):

    name = RequiredParameter(default="SynthGRB")
    z = RequiredParameter(default=1, vmin=0, vmax=20)
    T0 = RequiredParameter(default=0)
    ra = RequiredParameter(default=0, vmin=0, vmax=360)
    dec = RequiredParameter(default=0, vmin=-90, vmax=90)
    duration = RequiredParameter(default=1, vmin=0)

    def __init__(
        self,
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
        self._required_params = {}

        # create an empty list for the light curves
        # eetc
        self._lightcurves = collections.OrderedDict()
        self._responses = collections.OrderedDict()
        self._backgrounds = collections.OrderedDict()

        assert issubclass(source_function_class, SourceFunction)
        self._source_function = source_function_class

        # now set any source parameters that were passed

        for k, v in kwargs.items():

            if k in self._parameter_names:

                logger.debug(f"setting source param {k}: {kwargs[k]}")

                self._source_params[k] = kwargs[k]

                # make sure this is valid

                getattr(self, k)

            elif k in self._required_names:

                logger.debug(f"\setting required param {k}: {kwargs[k]}")

                self._required_params[k] = kwargs[k]

                # make sure this is valid
                getattr(self, k)

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

        list(self._lightcurves.values())[
            0
        ].display_energy_dependent_light_curve(
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

        list(self._lightcurves.values())[
            0
        ].display_time_dependent_spectrum(
            time=time, energy=energy, ax=ax, cmap=cmap, **kwargs
        )

    def display_energy_integrated_light_curve(self, time, ax=None, **kwargs):
        """FIXME! briefly describe function

        :param time:
        :param ax:
        :rtype:
        :returns:

        """

        list(self._lightcurves.values())[
            0
        ].display_energy_integrated_light_curve(time=time, ax=ax, **kwargs)

    def go(self, client=None, serial=False):

        for key in self._required_names:
            assert (
                self._required_params[key] is not None
            ), f"you have not set {key}"

        assert self.z > 0, f"z: {self.z} must be greater than zero"
        assert (
            self.duration > 0
        ), f"duration: {self.duration} must be greater than zero"

        logger.debug(f"created a GRB with name: {self.name}")
        logger.debug(f"created a GRB with ra: {self.ra} and dec: {self.dec}")
        logger.debug(f"created a GRB with redshift: {self.z}")
        logger.debug(
            f"created a GRB with duration: {self.duration} and T0: {self.T0}"
        )

        if not serial:

            if client is not None:

                futures = client.map(
                    process_lightcurve, self._lightcurves.values()
                )

                results = client.gather(futures)

            else:

                with worker_client() as client:

                    futures = client.map(
                        process_lightcurve, self._lightcurves.values()
                    )

                    results = client.gather(futures)

            del futures

        else:

            results = [
                process_lightcurve(lc) for lc in self._lightcurves.values()
            ]

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
            f.attrs["grb_name"] = self.name
            f.attrs["n_lightcurves"] = len(self._lightcurves)
            f.attrs["T0"] = self.T0
            f.attrs["z"] = self.z
            f.attrs["duration"] = self.duration
            f.attrs["ra"] = self.ra
            f.attrs["dec"] = self.dec

            # store the source function parameters

            recursively_save_dict_contents_to_group(
                f, "source", self._source_params
            )

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

                total_group.create_dataset(
                    "pha", data=lc.pha, compression="lzf"
                )
                total_group.create_dataset(
                    "times", data=lc.times, compression="lzf"
                )

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
                rsp_group.attrs[
                    "geometric_area"
                ] = lightcurve.response.geometric_area

            if clean_up:

                self._lightcurves.clear()

    def __repr__(self):

        return self._output().to_string()

    def info(self):

        self._output(as_display=True)

    def _output(self, as_display=False):

        std_dict = collections.OrderedDict()

        std_dict["name"] = self.name
        std_dict["z"] = self.z
        std_dict["ra"] = self.ra
        std_dict["dec"] = self.dec
        std_dict["duration"] = self.duration
        std_dict["T0"] = self.T0

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
