import numpy as np
import numba as nb
import os

from gbmgeometry import PositionInterpolator, GBM
from gbm_drm_gen import DRMGenTTE

from astropy.coordinates import SkyCoord

from cosmogrb.utils.package_utils import get_path_of_data_file


# def _sample_response()


@nb.njit(fastmath=True)
def _digitize(photon_energies, energy_edges, total_probability, cum_matrix):

    pha_channels = np.zeros(len(photon_energies))
    detections = np.zeros(len(photon_energies))

    for i in range(len(photon_energies)):

        idx = np.searchsorted(energy_edges, photon_energies[i]) - 1
        p_total = total_probability[idx]

        detected = False
        pha = -99

        # get a uniform random number

        r = np.random.random()

        if r > p_total:

            # get the pha channel from the cumulative distribution

            pha = int(np.abs(cum_matrix[idx] - r).argmin())

            detected = True

            pha_channels[i] = pha
            detections[i] = detected

    return pha_channels, detections


class Response(object):
    def __init__(self, matrix, geometric_area, energy_edges, channel_edges=None):

        self._matrix = matrix
        self._energy_edges = energy_edges
        self._channel_edges = channel_edges
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

        return self._effective_area

    def get_photon_bin(self, energy):

        return np.searchsorted(self._energy_edges, energy) - 1

    def _construct_probabilities(self):

        self._probability_matrix = self._matrix / self._geometric_area
        # self._probability_matrix = self._matrix

        # sum along the response to get the
        # the total probability in each photon bin
        self._total_probability_per_bin = self._probability_matrix.sum(axis=1)

        # np.linalg.norm(self._probability_matrix, axis=1, keepdims=True)

        non_zero_idx = self._total_probability_per_bin > 0

        # needs to be non zero... fix later
        self._normed_probability_matrix = self._probability_matrix

        self._normed_probability_matrix[np.where(non_zero_idx)[0], :] = (
            self._normed_probability_matrix[np.where(non_zero_idx)[0], :]
            / self._total_probability_per_bin[non_zero_idx, np.newaxis]
        )

        self._detection_probability = 1 - np.exp(-self._total_probability_per_bin)

        self._cumulative_maxtrix = np.cumsum(self._normed_probability_matrix, axis=1)

    def digitize(self, photon_energies):
        """
        digitze the photon into a energy bin
        via the energy dispersion

        :param photon_energy: 
        :returns: (pha_channel, detected)
        :rtype: 

        """

        np.random.seed()

        pha_channels, detections = _digitize(
            photon_energies,
            self._energy_edges,
            self._detection_probability,
            self._cumulative_maxtrix,
        )

        return pha_channels, detections

    @property
    def energy_edges(self):
        return self._energy_edges

    @property
    def channel_edges(self):
        return self._channel_edges

    def set_function(self, integral_function=None):
        """
        Set the function to be used for the convolution
        
        :param integral_function: a function f = f(e1,e2) which returns the integral of the model between e1 and e2
        :type integral_function: callable
        """

        self._integral_function = integral_function

    def convolve(self, t1, t2):

        true_fluxes = np.array(
            [
                self._integral_function(
                    self._energy_edges[i], self._energy_edges[i + 1], t1, t2
                )
                for i in range(len(self._energy_edges) - 1)
            ]
        )

        # Sometimes some channels have 0 lenths, or maybe they start at 0, where
        # many functions (like a power law) are not defined. In the response these
        # channels have usually a 0, but unfortunately for a computer
        # inf * zero != zero. Thus, let's force this. We avoid checking this situation
        # in details because this would have a HUGE hit on performances

        idx = np.isfinite(true_fluxes)
        true_fluxes[~idx] = 0

        folded_counts = np.dot(true_fluxes, self._matrix)

        return folded_counts


# These are just here for the position interpolator we used

_T0 = 576201540.940077

_Tmax = 576288060.940076

_pos_interp = PositionInterpolator(
    poshist=get_path_of_data_file("posthist.fit"), T0=_T0
)

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

        assert time + _T0 < _Tmax, "the time specified is out of bounds for the poshist"

        self._ra = ra
        self._dec = dec
        self._time = time

        self._detector_name = detector_name

        # compute the trigger time
        self._trigger_time = time + _T0

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

    def _setup_gbm_geometry(self, detector_name, ra, dec, time):

        # create a gbm for this time

        gbm = GBM(_pos_interp.quaternion(time), _pos_interp.sc_pos(time))

        # get the detector
        detector = gbm.detectors[detector_name]

        # make a scky coordinate
        coord = SkyCoord(ra, dec, unit="deg", frame="icrs")

        # get the detector center
        self._detector_center = detector.center

        # computer the seperation angle in rad
        self._separation_angle = np.deg2rad(
            self._detector_center.separation(coord).value
        )

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
            det_name=_det_translate[detector_name],
            time=time,
            T0=_T0,
            cspecfile=get_path_of_data_file(
                os.path.join("gbm_cspec", f"{detector_name}.pha")
            ),
            poshist=get_path_of_data_file("posthist.fit"),
            mat_type=2,
        )

        if self._save:
            drm_gen.to_fits(
                ra, dec, f"{self._name}_{detector_name}.rsp", overwrite=True
            )

        else:
            drm_gen.set_location(ra, dec)

        return drm_gen.matrix.T, drm_gen.monte_carlo_energies, drm_gen.ebounds

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
        return _T0

    @property
    def detector_name(self):
        return self._detector_name

    def write_rsp(self, file_name):
        """
        save the generated response to 
        a file

        :param file_name: 
        :returns: 
        :rtype: 

        """

        self._drm_gen.to_fits(self._ra, self._dec, file_name, overwrite=True)


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


__all__ = ["Response", "BGOResponse", "NaIResponse"]
