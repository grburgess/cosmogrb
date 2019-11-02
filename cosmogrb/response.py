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


        probability_matrix =  self._matrix / self._geometric_area 

        # sum along the response to get the
        # the total probability in each photon bin
        total_probability_per_bin = probability_matrix.sum(axis=1)

        non_zero_idx = total_probability_per_bin > 0

        # needs to be non zero... fix later
        normed_probability_matrix = np.divide(probability_matrix,total_probability_per_bin)
        

    
    def digitize(self, photon_energy):
        """
        digitze the photon into a energy bin
        via the energy dispersion

        :param photon_energy: 
        :returns: 
        :rtype: 

        """

        idx = self.get_photon_bin(photon_energy)

        

    
    
class GBMResponse(Response):
    def __init__(self, radius, height):
        
        
        
        self._radius =  radius
        self._height = height


        super(GBMResponse, self).__init__()

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


class NaIResponse(GBMResponse):
    def __init__(self):

        super(NaIResponse, self).__init__(radius = 0.5 * 12.7,
                                          height = 1.27
                                          
        )


class BGOResponse(GBMResponse):
    def __init__(self):

        super(BGOResponse, self).__init__(radius = 0.5 * 12.7
                                          height = 12.7
        )

    def _compute_geometric_area(self, angle):

        super(BGOResponse, self)._compute_geometric_area(angle + 0.5 * np.pi)
        

__all__ = ["Response", "BGOResponse", "NaIResponse"]
