import os

import numpy as np
from astropy.coordinates import SkyCoord
from gbmgeometry import PositionInterpolator, gbm_detector_list

from cosmogrb import cosmogrb_config
from cosmogrb.instruments.gbm.gbm_orbit import gbm_orbit
from cosmogrb.instruments.gbm.response_generator import gbm_response_generator
from cosmogrb.response.response import Response
from cosmogrb.utils.package_utils import get_path_of_data_file

# These are just here for the position interpolator we used


_det_translate = dict(
    n0="NAI_00",
    n1="NAI_01",
    n2="NAI_02",
    n3="NAI_03",
    n4="NAI_04",
    n5="NAI_05",
    n6="NAI_06",
    n7="NAI_07",
    n8="NAI_08",
    n9="NAI_09",
    na="NAI_10",
    nb="NAI_11",
    b0="BGO_00",
    b1="BGO_01",
)



class GBMResponse(Response):
    def __init__(
        self,
        detector_name: str,
        ra: float,
        dec: float,
        radius: float,
        height: float,
        rng: np.random._generator.Generator,
        save: float = False,
        name=None,
    ):
        """

        A generic GBM reponse that builds itself from the response
        generator

        :param detector_name:
        :param ra:
        :param dec:
        :param radius:
        :param height:
        :param save:
        :param name:
        :returns:
        :rtype:

        """

        self._radius: float = radius
        self._height: float = height

        # if the config is set to use random times, the we
        # get a _relative_ time to the being of the posthist
        # MET, i.e., time = MET - T0. Thus, we get a relative
        # time in the orbit

        if cosmogrb_config["gbm"]["orbit"]["use_random_time"]:

            # make sure to put all detectors at same position 
            # in orbit by passing random number generator

            time: float = gbm_orbit.random_time(rng)

        else:

            # if we want a fixed time, then choose the default

            time = cosmogrb_config.gbm.orbit.default_time

        # we pass this time to the repsonse generator. Note, our local
        # time is for the GRB will be at T0, but the response generator
        # will have its T0 at the the minimum of the posthist and thus,

        # we still need the relative time

        self._time: float = time

        self._setup_gbm_geometry(detector_name, ra, dec)

        # tmin, tmax = gbm_orbit.position_interpolator.minmax_time()

        # assert time < tmax, "the time specified is out of bounds for the poshist"

        self._ra: float = ra
        self._dec: float = dec

        self._detector_name: str = detector_name

        # compute the trigger time
        self._trigger_time: float = gbm_orbit.met(time)

        if save:
            assert name is not None, "if you want to save, you must have a name"

        self._save: bool = save
        self._name: str = name

        geometric_area: float = self._compute_geometric_area()

        matrix, energy_edges, channel_edges = self._create_matrix(
            detector_name, ra, dec
        )

        super(GBMResponse, self).__init__(
            matrix=matrix,
            geometric_area=geometric_area,
            energy_edges=energy_edges,
            channel_edges=channel_edges,
        )

        if self._save:
            self.to_fits(f"{self._name}_{detector_name}.rsp", overwrite=True)

    def _setup_gbm_geometry(
        self, detector_name: str, ra: float, dec: float
    ) -> None:

        # get the detector
        detector = gbm_detector_list[detector_name](
            sc_pos=gbm_orbit.position_interpolator.sc_pos(self._time),
            quaternion=gbm_orbit.position_interpolator.quaternion(self._time),
        )

        # make a scky coordinate
        coord = SkyCoord(ra, dec, unit="deg", frame="icrs")

        # get the detector center
        self._detector_center = detector.center

        # computer the seperation angle in rad
        self._separation_angle = np.deg2rad(
            self._detector_center.separation(coord).value
        )

    @property
    def separation_angle(self) -> float:
        return np.rad2deg(self._separation_angle)

    def _compute_geometric_area(self) -> None:
        """
        compute the geometric area of the detector
        for a given viewing angle

        :param angle:
        :returns:
        :rtype:

        """

        return np.fabs(
            np.pi * (self._radius ** 2) * np.cos(self._separation_angle)
        ) + np.fabs(
            2 * self._radius * self._height * np.sin(self._separation_angle)
        )

    def _create_matrix(self, detector_name, ra, dec):
        """
        Create the response matrix for the given time and location

        :param detector_name:
        :param ra:
        :param dec:
        :param time:
        :returns:
        :rtype:

        """

        # since this is now done with a singleton it
        # may cause some race conditions

        # gbm_response_generator.set_time(self._time, detector_name)
        # matrix = gbm_response_generator.set_location(ra, dec, detector_name)

        matrix = gbm_response_generator.generate_response(
            ra, dec, self._time, detector_name
        )

        return (
            matrix,
            gbm_response_generator.mc_energies[detector_name],
            gbm_response_generator.ebounds[detector_name],
        )

    @property
    def ra(self) -> float:
        return self._ra

    @property
    def dec(self) -> float:
        return self._dec

    @property
    def time(self) -> float:
        return self._time

    @property
    def trigger_time(self) -> float:
        return self._trigger_time

    @property
    def T0(self):

        # THIS MIGHT BE WRONG!
        return gbm_orbit.met(self._time)

    @property
    def detector_name(self) -> str:
        return self._detector_name

    def to_fits(self, file_name, overwrite=True) -> None:
        """
        save the generated response to
        a file

        :param file_name:
        :returns:
        :rtype:

        """

        super(GBMResponse, self).to_fits(
            file_name,
            telescope_name="fermi",
            instrument_name=self._detector_name,
            overwrite=overwrite,
        )


class NaIResponse(GBMResponse):
    def __init__(self, detector_name, ra, dec, rng, save=False, name=None):

        super(NaIResponse, self).__init__(
            ra=ra,
            dec=dec,
            detector_name=detector_name,
            radius=0.5 * 12.7,
            height=1.27,
            rng=rng,
            save=save,
            name=name,
        )


class BGOResponse(GBMResponse):
    def __init__(self, detector_name, ra, dec, rng, save=False, name=None):

        super(BGOResponse, self).__init__(
            detector_name=detector_name,
            ra=ra,
            dec=dec,
            radius=0.5 * 12.7,
            height=12.7,
            rng=rng,
            save=save,
            name=name,
        )

    def _compute_geometric_area(self):

        # super(BGOResponse, self)._compute_geometric_area(self._separation_angle + 0.5 * np.pi)

        # this may be wrong

        return np.fabs(
            np.pi
            * (self._radius ** 2)
            * np.cos(self._separation_angle + 0.5 * np.pi)
        ) + np.fabs(
            2
            * self._radius
            * self._height
            * np.sin(self._separation_angle + 0.5 * np.pi)
        )


__all__ = ["BGOResponse", "NaIResponse"]
