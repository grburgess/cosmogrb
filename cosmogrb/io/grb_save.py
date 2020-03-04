import h5py
from cosmogrb.lightcurve.lightcurve import LightCurveStorage
from cosmogrb.response import Response


class GRBSave(object):
    def __init__(self, grb_name, lightcurves, responses):
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

        self._internal_storage = dict()

        for key in lightcurves.keys():

            self._internal_storage[key] = dict(
                lightcurve=lightcurves[key], response=responses[key]
            )

        self._name = grb_name

    def __getitem__(self, key):

        if key in self._internal_storage:

            return self._internal_storage[key]

        else:

            raise ValueError(f"{key} is not in th GRB")

    @property
    def name(self):
        return self._name

    @classmethod
    def from_file(cls, file_name):

        lightcurves = dict()
        responses = dict()

        with h5py.File(file_name, "r") as f:

            grb_name = f.attrs["grb_name"]

            det_group = f["detectors"]

            for lc_name in det_group.keys():

                lc_group = det_group[lc_name]

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
                    pha=pha,
                    times=times,
                    times_source=times_source,
                    pha_source=pha_source,
                    times_background=times_background,
                    pha_background=pha_background,
                    channels=rsp.channels,
                    ebounds=rsp.channel_edges,
                )

                lightcurves[lc_name] = lc_container

        return cls(grb_name=grb_name, lightcurves=lightcurves, responses=responses)
