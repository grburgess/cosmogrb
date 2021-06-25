import numba as nb
import numpy as np
from numba.core import types
from numba.typed import Dict

from cosmogrb.utils.interpolation import Interp1D
from cosmogrb.utils.response_file import RSP


@nb.njit(fastmath=True, cache=False)
def _digitize(photon_energies, energy_edges, cum_matrix):

    pha_channels = np.zeros(len(photon_energies))
    for i in range(len(photon_energies)):
        idx = np.searchsorted(energy_edges, photon_energies[i]) - 1

        # get a uniform random number
        r = np.random.random()

        # get the pha channel from the cumulative distribution
        pha = int(np.abs(cum_matrix[idx] - r).argmin())

        pha_channels[i] = pha

    return pha_channels


class Response(object):
    def __init__(
        self,
        matrix,
        geometric_area,
        energy_edges,
        channel_edges=None,
        channel_starts_at=0,
        separation_angle=0
    ):

        self._matrix = matrix.astype('f8')
        self._energy_edges = energy_edges.astype('f8')
        self._energy_width = np.diff(self._energy_edges)
        self._energy_mean = (
            self._energy_edges[:-1] + self._energy_edges[1:]) / 2.0

        self._emin = self._energy_edges[0]
        self._emax = self._energy_edges[-1]
        
        self._channel_edges = channel_edges.astype('f8')
        self._channel_width = np.diff(self._channel_edges)
        self._channel_mean = (
            self._channel_edges[:-1] + self._channel_edges[1:]) / 2.0

        self._channels = np.arange(len(self._channel_width), dtype=np.int64)

        self._separation_angle = separation_angle
        
        self._build_effective_area_curve()

        self._geometric_area = geometric_area

        self._construct_probabilities()

    # def effective_area(self, energy):
    #     """
    #     The effective area of the detector
    #     in cm^2

    #     :returns:
    #     :rtype:

    #     """

    #     return self._effective_area(energy)

    def _build_effective_area_curve(self):

        # first compute the effective area curve
        # by summing over the matrix and then create
        # and interpolation for later

        ea_curve = self._matrix.sum(axis=1)

        # we just a numba jitclass to interpolate
        # we want this passable to functions locally

        self.effective_area = Interp1D(
            self._energy_mean,
            ea_curve,
            self._energy_mean.min(),
            self._energy_mean.max()
        )

        # However is very difficult to serialize
        # this shit. So, some functions may just want
        # to do the interpolation themselves. We pack
        # these variables up for that

        # self.effective_area_dict = Dict.empty(
        #     key_type=types.unicode_type,
        #     value_type=types.float64[:]
        # )

        # The typed-dict can be used from the interpreter.

        # NOTE: you can't pickle these fucking things..
        # self.effective_area_dict["mean_energy"] = self._energy_mean
        # self.effective_area_dict["ea_curve"] = ea_curve

        # we do not want zeros
        
        idx = ea_curve>0.
        
        ea_curve[~idx] = 1.e-99

        self.effective_area_packed = np.vstack((self._energy_mean, ea_curve))
        
        idx = ea_curve[:-10].argmax()
        self._max_energy = self._energy_mean[idx]

    @property
    def effective_area_max(self):
        return self._max_energy

    @property
    def separation_angle(self) -> float:
        return np.rad2deg(self._separation_angle)

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

        self._detection_probability = 1 - \
            np.exp(-self._total_probability_per_bin)

        self._cumulative_maxtrix = np.cumsum(
            self._normed_probability_matrix, axis=1)

    def digitize(self, photon_energies):
        """
        digitze the photon into a energy bin
        via the energy dispersion

        :param photon_energy: 
        :returns: (pha_channel, detected)
        :rtype: 

        """

        np.random.seed()

        pha_channels = _digitize(
            photon_energies, self._energy_edges, self._cumulative_maxtrix,
        )
        return pha_channels

    @property
    def energy_edges(self):
        return self._energy_edges


    @property
    def emin(self):
        return self._emin

    @property
    def emax(self):
        return self._emax
    
    @property
    def channel_edges(self):
        return self._channel_edges

    @property
    def channels(self):
        return self._channels

    @property
    def matrix(self):
        return self._matrix

    @property
    def geometric_area(self):
        return self._geometric_area

    def set_function(self, integral_function=None):
        """
        Set the function to be used for the convolution

        :param integral_function: a function f = f(e1,e2) which returns the integral of the model between e1 and e2
        :type integral_function: callable
        """

        self._integral_function = integral_function

    def convolve(self):

        # true_fluxes = np.array(
        #     [
        #         self._integral_function(
        #             self._energy_edges[i], self._energy_edges[i + 1]
        #         )
        #         for i in range(len(self._energy_edges) - 1)
        #     ]
        # )

        true_fluxes = self._integral_function(self._energy_edges)
        
        # Sometimes some channels have 0 lenths, or maybe they start at 0, where
        # many functions (like a power law) are not defined. In the response these
        # channels have usually a 0, but unfortunately for a computer
        # inf * zero != zero. Thus, let's force this. We avoid checking this situation
        # in details because this would have a HUGE hit on performances

        idx = np.isfinite(true_fluxes)
        true_fluxes[~idx] = 0

        folded_counts = np.dot(true_fluxes, self._matrix)

        return folded_counts

    def to_fits(
        self,
        filename,
        telescope_name="telescope",
        instrument_name="detector",
        overwrite=False,
    ):
        """
        Write the current matrix into a OGIP FITS file
        :param filename : the name of the FITS file to be created
        :type filename : str
        :param telescope_name : a name for the telescope/experiment which this matrix applies to
        :param instrument_name : a name for the instrument which this matrix applies to
        :param overwrite: True or False, whether to overwrite or not the output file
        :return: None
        """

        fits_file = RSP(
            self._energy_edges,
            self._channel_edges,
            self.matrix.T,  # we transpose teh matrix earlier for speed
            telescope_name,
            instrument_name,
        )

        fits_file.writeto(filename, clobber=overwrite)


__all__ = ["Response"]
