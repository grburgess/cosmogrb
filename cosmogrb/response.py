import numpy as np


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


class GBMResponse(Response):
    def __init__(self, file_name, radius, height, angle):

        self._radius = radius
        self._height = height

        geomtric_area = self._compute_geometric_area(angle)

        matrix = self._read_matrix(file_name)

        super(GBMResponse, self).__init__(matrix=matrix, geomtric_area=geomtric_area)

    def _compute_geometric_area(self, angle):
        """
        compute the geometric area of the detector
        for a given viewing angle

        :param angle: 
        :returns: 
        :rtype: 

        """

        return np.fabs(np.pi * (self._radius ** 2) * np.cos(angle)) + np.fabs(
            2 * self._radius * self._height * np.sin(angle)
        )


    def _read_matrix(self, file_name):
        """
        read a 

        :param file_name: 
        :returns: 
        :rtype: 

        """
        
        pass


        
    
class NaIResponse(GBMResponse):
    def __init__(self, file_name, angle):

        super(NaIResponse, self).__init__(
            file_name=file_name, angle=angle, radius=0.5 * 12.7, height=1.27
        )


class BGOResponse(GBMResponse):
    def __init__(self, file_name, angle):

        super(BGOResponse, self).__init__(
            file_name=file_name, angle=angle, radius=0.5 * 12.7, height=12.7
        )

    def _compute_geometric_area(self, angle):

        super(BGOResponse, self)._compute_geometric_area(angle + 0.5 * np.pi)


__all__ = ["Response", "BGOResponse", "NaIResponse"]
