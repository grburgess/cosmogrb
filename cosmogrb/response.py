import numpy as np
import os

from gbmgeometry import PositionInterpolator, GBM
from gbm_drm_gen import DRMGenTTE

from astropy.coordinates import SkyCoord

from cosmogrb.utils.package_utils import get_path_of_data_file


class Response(object):
    def __init__(self, matrix, geometric_area):

        self._matrix = matrix
        self._geometric_area = geometric_area

        self._construct_probabilities()

    @property
    def effective_area(self):
        """
        The effective area of the detector
        in cm^2

        :returns: 
        :rtype: 

        """

        return self.effective_area

    def _construct_probabilities(self):

        self._probability_matrix = self._matrix / self._geometric_area

        # sum along the response to get the
        # the total probability in each photon bin
        self._total_probability_per_bin = self._probability_matrix.sum(axis=1)

        non_zero_idx = self._total_probability_per_bin > 0

        # needs to be non zero... fix later
        self._normed_probability_matrix = np.divide(
            self._probability_matrix, self._total_probability_per_bin
        )

        self._cumulative_maxtrix = np.cumsum(self._normed_probability_matrix, axis=1)

    def digitize(self, photon_energy):
        """
        digitze the photon into a energy bin
        via the energy dispersion

        :param photon_energy: 
        :returns: (pha_channel, detected)
        :rtype: 

        """

        # figure out which photon bin we have

        idx = self.get_photon_bin(photon_energy)

        p_total = self._total_probability_per_bin[idx]

        # initially the photon is not detected
        # and the channel is set to a dummy number
        detected = False
        pha_channel = -99

        while p_total > 0.0:

            # get a uniform random number

            r = np.random.random()

            if r < p_total:

                # get the pha channel from the cumulative distribution
                pha_channel = np.abs(self._cumulative_maxtrix[idx] - r).argmin()

                detected = True

            p_total -= 1

        return pha_channel, np.array(detected)


_T0 = 576201540.940077
_pos_interp = PositionInterpolator(
    poshist=get_path_of_data_file("posthist.fit"), T0=_T0
)


class GBMResponse(Response):
    def __init__(self, detector_name, ra, dec, time, radius, height):

        self._radius = radius
        self._height = height

        self._setup_gbm_geometry(detector_name, ra, dec, time)

        self._create_matrix(detector_name, ra, dec, time)

        geomtric_area = self._compute_geometric_area(angle)

        matrix = self._read_matrix(detector_name, ra, dec)

        super(GBMResponse, self).__init__(matrix=matrix, geomtric_area=geomtric_area)

    def _setup_gbm_geometry(self, detector_name, ra, dec, time):

        # create a gbm for this time

        gbm = GBM(_pos_interp.quaternion(time), _pos_interp.sc_pos(time))

        # get the detector
        detector = gbm.detectors[detector_name]

        # make a scky coordinate
        coord = SkyCoord(ra, dec, unit="deg", frame="icrs")

        # get the detector center
        detector_center = detector.center

        # computer the seperation angle in rad
        self._seperation_angle = np.deg2rad(detector_center.separation(coord).value)

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

        drm_gen = DRMGenTTE(
            det_name=det_translate[detector_name],
            time=time,
            T0=_T0,
            cspecfile=get_path_of_data_file(
                os.path.join("gbm_cspec", f"{detector_name}.pha")
            ),
            posthist=get_path_of_data_file("posthist.fit"),
            mat_type=2,
        )

        drm_gen.set_location(ra, dec)

        return drm_gen.matrix


class NaIResponse(GBMResponse):
    def __init__(self, detector_name, ra, dec, time):

        super(NaIResponse, self).__init__(
            ra=ra,
            dec=dec,
            time=time,
            detector_name=detector_name,
            radius=0.5 * 12.7,
            height=1.27,
        )


class BGOResponse(GBMResponse):
    def __init__(self, detector_name, ra, dec, time):

        super(BGOResponse, self).__init__(
            detector_name=detector_name,
            ra=ra,
            dec=dec,
            time=time,
            radius=0.5 * 12.7,
            height=12.7,
        )

    def _compute_geometric_area(self, angle):

        super(BGOResponse, self)._compute_geometric_area(angle + 0.5 * np.pi)


__all__ = ["Response", "BGOResponse", "NaIResponse"]
