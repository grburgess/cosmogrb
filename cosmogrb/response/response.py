import numpy as np
import numba as nb

from scipy.interpolate import interp1d

from cosmogrb.utils.response_file import RSP


@nb.njit(fastmath=True)
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
    ):

        self._matrix = matrix
        self._energy_edges = energy_edges
        self._energy_width = np.diff(energy_edges)
        self._energy_mean = (energy_edges[:-1] + energy_edges[1:]) / 2.0

        self._channel_edges = channel_edges
        self._channel_width = np.diff(channel_edges)
        self._channel_mean = (channel_edges[:-1] + channel_edges[1:]) / 2.0

        self._channels = np.arange(len(self._channel_width), dtype=np.int64)

        self._build_effective_area_curve()

        self._geometric_area = geometric_area

        self._construct_probabilities()

    def effective_area(self, energy):
        """
        The effective area of the detector
        in cm^2

        :returns: 
        :rtype: 

        """

        return self._effective_area(energy)

    def _build_effective_area_curve(self):

        # first compute the effective area curve
        # by summing over the matrix and then create
        # and interpolation for later

        ea_curve = self._matrix.sum(axis=1)

        self._effective_area = interp1d(
            self._energy_mean,
            self._matrix.sum(axis=1),
            kind="cubic",
            bounds_error=False,
            fill_value=0.0,
        )

        idx = ea_curve[:-10].argmax()
        self._max_energy = self._energy_mean[idx]

    @property
    def effective_area_max(self):
        return self._max_energy

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

        pha_channels = _digitize(
            photon_energies, self._energy_edges, self._cumulative_maxtrix,
        )
        return pha_channels

    @property
    def energy_edges(self):
        return self._energy_edges

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
            self.matrix.T, # we transpose teh matrix earlier for speed
            telescope_name,
            instrument_name,
        )

        fits_file.writeto(filename, clobber=overwrite)



__all__ = ["Response"]
