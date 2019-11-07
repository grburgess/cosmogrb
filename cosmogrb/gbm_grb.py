from gbmgeometry import GBM
import multiprocessing as mp


from cosmogrb.lightcurve import GBMLightCurve









class GBMGRB(object):

    _background_start = -100
    _background_stop = 300
    

    def __init__(self, ra, dec, z, peak_flux, alpha, ep, tau, trise, duration ):

        self._ra = ra
        self._dec = dec
        self._z = z
        self._alpha = alpha
        self._ep = ep
        self._trise = trise
        self._duration = duration

        
    
