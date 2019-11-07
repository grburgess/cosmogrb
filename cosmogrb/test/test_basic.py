from cosmogrb.lightcurve.background import GBMBackground
from cosmogrb.utils.package_utils import get_path_of_data_file

from cosmogrb.response import NaIResponse

from cosmogrb.lightcurve.cpl_source import CPLSourceFunction, norris
from cosmogrb.lightcurve.source import Source, evolution_sampler
from cosmogrb.lightcurve.lightcurve import GBMLightCurve


def test_basic_gbm():

    bkg = GBMBackground(-50, 50, average_rate=100.0, detector="n1")
    nai = NaIResponse("n1", 312.0, -62.0, 1)
    cpl = CPLSourceFunction(peak_flux=1e-5, trise=0.5, tdecay=5)
    source = Source(0.0, 10.0, cpl)

    lc = GBMLightCurve(source, bkg, nai)

    lc.process()
