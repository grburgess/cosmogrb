import numpy as np
import os
from gbmgeometry import PositionInterpolator, gbm_detector_list


from astropy.coordinates import SkyCoord

from cosmogrb.utils.package_utils import get_path_of_data_file

from cosmogrb.response.response import Response
from cosmogrb.instruments.gbm.gbm_orbit import gbm_orbit
from cosmogrb.instruments.gbm.response_generator import gbm_response_generator

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
        self, detector_name, ra, dec, time, radius, height, save=False, name=None
    ):

        self._radius = radius
        self._height = height

        self._setup_gbm_geometry(detector_name, ra, dec, time)

        tmin, tmax = gbm_orbit.position_interpolator.minmax_time()

        assert time < tmax, "the time specified is out of bounds for the poshist"

        self._ra = ra
        self._dec = dec
        self._time = time

        self._detector_name = detector_name

        # compute the trigger time
        self._trigger_time = gbm_orbit.met(time)

        if save:
            assert name is not None, "if you want to save, you must have a name"

        self._save = save
        self._name = name

        geometric_area = self._compute_geometric_area()

        matrix, energy_edges, channel_edges = self._create_matrix(
            detector_name, ra, dec, time
        )

        super(GBMResponse, self).__init__(
            matrix=matrix,
            geometric_area=geometric_area,
            energy_edges=energy_edges,
            channel_edges=channel_edges,
        )

        if self._save:
            self.to_fits(f"{self._name}_{detector_name}.rsp", overwrite=True)

    def _setup_gbm_geometry(self, detector_name, ra, dec, time):

        # get the detector
        detector = gbm_detector_list[detector_name](
            sc_pos=gbm_orbit.position_interpolator.sc_pos(time),
            quaternion=gbm_orbit.position_interpolator.quaternion(time),
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
    def separation_angle(self):
        return np.rad2deg(self._separation_angle)

    def _compute_geometric_area(self):
        """
        compute the geometric area of the detector
        for a given viewing angle

        :param angle: 
        :returns: 
        :rtype: 

        """

        return np.fabs(
            np.pi * (self._radius ** 2) * np.cos(self._separation_angle)
        ) + np.fabs(2 * self._radius * self._height * np.sin(self._separation_angle))

    def _create_matrix(self, detector_name, ra, dec, time):
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

        gbm_response_generator.set_time(time, detector_name)
        matrix = gbm_response_generator.set_location(ra, dec, detector_name)

        return (
            matrix,
            gbm_response_generator.mc_energies[detector_name],
            gbm_response_generator.ebounds[detector_name],
        )

    @property
    def ra(self):
        return self._ra

    @property
    def dec(self):
        return self._dec

    @property
    def time(self):
        return self._time

    @property
    def trigger_time(self):
        return self._trigger_time

    @property
    def T0(self):
        return gbm_orbit.T0

    @property
    def detector_name(self):
        return self._detector_name

    def to_fits(self, file_name, overwrite=True):
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
    def __init__(self, detector_name, ra, dec, time, save=False, name=None):

        super(NaIResponse, self).__init__(
            ra=ra,
            dec=dec,
            time=time,
            detector_name=detector_name,
            radius=0.5 * 12.7,
            height=1.27,
            save=save,
            name=name,
        )


class BGOResponse(GBMResponse):
    def __init__(self, detector_name, ra, dec, time, save=False, name=None):

        super(BGOResponse, self).__init__(
            detector_name=detector_name,
            ra=ra,
            dec=dec,
            time=time,
            radius=0.5 * 12.7,
            height=12.7,
            save=save,
            name=name,
        )

    def _compute_geometric_area(self):

        # super(BGOResponse, self)._compute_geometric_area(self._separation_angle + 0.5 * np.pi)

        # this may be wrong

        return np.fabs(
            np.pi * (self._radius ** 2) * np.cos(self._separation_angle + 0.5 * np.pi)
        ) + np.fabs(
            2
            * self._radius
            * self._height
            * np.sin(self._separation_angle + 0.5 * np.pi)
        )


__all__ = ["BGOResponse", "NaIResponse"]
