import h5py
import collections
import pandas as pd
from IPython.display import display
from cosmogrb.utils.hdf5_utils import recursively_load_dict_contents_from_group
from cosmogrb.lightcurve.light_curve_storage import LightCurveStorage
from cosmogrb.response.response import Response


class GRBSave(collections.UserDict):
    def __init__(
        self,
        grb_name,
        T0,
        ra,
        dec,
        duration,
        z,
        lightcurves,
        responses,
        source_params,
        extra_info=None,
    ):
        """

        :param grb_name: 
        :param lightcurves: 
        :param responses: 
        :returns: 
        :rtype: 

        """

        assert isinstance(
            lightcurves, dict
        ), "lightcurves must be a dict containing LightCurveStorage objects"

        assert isinstance(
            responses, dict
        ), "responses must be a dict containing Response objects"

        for k, v in lightcurves.items():

            assert isinstance(v, LightCurveStorage), print(
                f"{k} is not of type LightCurveStorage"
            )

        for k, v in responses.items():

            assert isinstance(v, Response), print(f"{k} is not of type Response")

        for key1, key2 in zip(responses.keys(), lightcurves.keys()):

            assert (
                key1 == key2
            ), f"{key1} is not {key2} so there is a mismatch between the responses and lightcurves"

        # ok, now lets build the objects

        # this allows us to set the dict
        self._lock_dict = False

        data = {}

        for key in lightcurves.keys():

            data[key] = dict(lightcurve=lightcurves[key], response=responses[key])

        #

        super(GRBSave, self).__init__(data)

        self._lock_dict = True

        assert isinstance(source_params, dict)
        self._source_params = source_params

        if extra_info is not None:
            assert isinstance(extra_info, dict)
        self._extra_info = extra_info

        self._name = grb_name
        self._T0 = T0
        self._ra = ra
        self._dec = dec
        self._z = z
        self._duration = duration

    def __setitem__(self, key, value):

        if self._lock_dict:
            raise RuntimeWarning("Cannot modify the internal data!")

        else:

            super(GRBSave, self).__setitem__(key, value)

    def __delitem__(self, key):

        if self._lock_dict:

            raise RuntimeWarning("Cannot modify the internal data!")

        else:

            super(GRBSave, self).__delitem__(key)

    @property
    def name(self):
        return self._name

    @property
    def ra(self):
        return self._ra

    @property
    def dec(self):
        return self._dec

    @property
    def z(self):
        return self._z

    @property
    def duration(self):
        return self._duration

    @property
    def T0(self):
        return self._T0

    @property
    def extra_info(self):
        return self._extra_info

    @property
    def source_params(self):
        return self._source_params

    @classmethod
    def from_file(cls, file_name):

        lightcurves = dict()
        responses = dict()

        with h5py.File(file_name, "r") as f:

            grb_name = f.attrs["grb_name"]

            ra = f.attrs["ra"]
            dec = f.attrs["dec"]
            T0 = f.attrs["T0"]
            z = f.attrs["z"]
            duration = f.attrs["duration"]

            source_params = recursively_load_dict_contents_from_group(f, "source")

            try:

                extra_info = recursively_load_dict_contents_from_group(f, "extra_info")

            except:

                extra_info = None

            det_group = f["detectors"]

            for lc_name in det_group.keys():

                lc_group = det_group[lc_name]

                tstart = lc_group.attrs["tstart"]
                tstop = lc_group.attrs["tstop"]
                time_adjustment = lc_group.attrs["time_adjustment"]
                instrument = lc_group.attrs["instrument"]

                try:
                    lc_extra_info = recursively_load_dict_contents_from_group(
                        f, f"{lc_name}/extra_info"
                    )

                except:
                    lc_extra_info = {}

                channels = lc_group["channels"]

                pha = lc_group["total_signal"]["pha"][()]
                times = lc_group["total_signal"]["times"][()]

                pha_source = lc_group["source_signal"]["pha"][()]
                times_source = lc_group["source_signal"]["times"][()]

                pha_background = lc_group["background_signal"]["pha"][()]
                times_background = lc_group["background_signal"]["times"][()]

                # now get the response info

                rsp_group = lc_group["response"]

                matrix = rsp_group["matrix"][()]
                energy_edges = rsp_group["energy_edges"][()]
                channel_edges = rsp_group["channel_edges"][()]
                geometric_area = rsp_group.attrs["geometric_area"]

                rsp = Response(
                    matrix=matrix,
                    geometric_area=geometric_area,
                    energy_edges=energy_edges,
                    channel_edges=channel_edges,
                )

                responses[lc_name] = rsp

                lc_container = LightCurveStorage(
                    name=lc_name,
                    tstart=tstart,
                    tstop=tstop,
                    time_adjustment=time_adjustment,
                    pha=pha,
                    times=times,
                    times_source=times_source,
                    pha_source=pha_source,
                    times_background=times_background,
                    pha_background=pha_background,
                    channels=rsp.channels,
                    ebounds=rsp.channel_edges,
                    T0=T0,
                    instrument=instrument,
                    extra_info=lc_extra_info,
                )

                lightcurves[lc_name] = lc_container

        return cls(
            grb_name=grb_name,
            T0=T0,
            ra=ra,
            dec=dec,
            z=z,
            duration=duration,
            lightcurves=lightcurves,
            responses=responses,
            source_params=source_params,
            extra_info=extra_info,
        )

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

            if self._extra_info:

                extra_df = pd.Series(
                    data=self._extra_info, index=self._extra_info.keys()
                )

                display(extra_df.to_frame())

        else:

            for k, v in self._source_params.items():
                std_dict[k] = v

            if self._extra_info:
                for k, v in self._extra_info.items():
                    std_dict[k] = v

        return pd.Series(data=std_dict, index=std_dict.keys())
