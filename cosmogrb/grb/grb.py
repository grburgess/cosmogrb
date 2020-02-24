import multiprocessing as mp


from cosmogrb.lightcurve import GBMLightCurve
from cosmogrb.sampler.source import Source
from cosmogrb.sampler.background import GBMBackground
from cosmogrb.sampler.cpl_source import CPLSourceFunction

from cosmogrb.sampler.constant_cpl import ConstantCPL

from cosmogrb.response import NaIResponse, BGOResponse



class GRB(object):

    def __init__(self, name='SynthGRB', verbose=False):

        self._verbose = verbose
        self._name = name

        self._lightcurves = []

    


    def _add_lightcurve(self, lightcurve):

        self._lightcurves.append(lightcurve)
        
    def go(self, n_cores=8):

        pool = mp.Pool(n_cores)

        pool.map(process_lightcurve, self._lightcurves)
        pool.close()
        pool.join()






        
def process_lightcurve(lc):
    lc.process()
