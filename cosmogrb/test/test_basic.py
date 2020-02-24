
from cosmogrb.grb import GBMGRB

def test_basic_gbm():

    grb = GBMGRB(ra=312., dec =-62. ,
             z=1.,
             peak_flux=5E-7, alpha= -.66, ep=500., 
             tau=2.,
             trise=1.,
             duration=20.,
             T0=0.1,
             
             verbose=True)

    grb.go(n_cores=1)
