import os
import numpy as np
from glob import glob
from cosmogrb.instruments.gbm import GBMGRB_CPL_Constant, GBMGRB, GBMGRB_CPL

from cosmogrb.io.grb_save import GRBSave
from cosmogrb.io.gbm_fits import grbsave_to_gbm_fits

from dask.distributed import Client, LocalCluster


import pytest

@pytest.fixture(scope='session')
def grb():
    grb = GBMGRB_CPL(ra=312.0,
                     dec=-62.0,
                     z=1.0,
                     peak_flux=5e-9,
                     alpha=-0.66,
                     ep=500.0,
                     tau=2.0,
                     trise=0.1,
                     tdecay=.5,
                     duration=1.0,
                     T0=0.1,
    )

    cluster = LocalCluster(n_workers=2)
    client = Client(cluster)
    
    grb.go(client=client)
    
    return grb

@pytest.fixture(scope='session')
def grb_constant():
    grb = GBMGRB_CPL_Constant(ra=312.0,
                     dec=-62.0,
                     z=1.0,
                     peak_flux=5e-9,
                     alpha=-0.66,
                     ep=500.0,
                     duration=1.0,
                     T0=0.1,
    )


    cluster = LocalCluster(n_workers=2)
    client = Client(cluster)
    
    grb.go(client=client)

    
    
    
    return grb







def test_gbm_constructor_and_plotting(grb):

    time = np.linspace(0, 20, 10)
    energy = np.logspace(1, 2, 10)

    grb.display_energy_dependent_light_curve(time, energy)
    grb.display_energy_integrated_light_curve(time)


# def test_gbm_process(grb):

    
    
#     files_to_remove = glob("SynthGRB*.rsp")

#     for f in files_to_remove:
#         os.remove(f)


def test_gbm_save(grb):

    grb.save("test.h5")



def test_read_gbm_save():

    grb = GRBSave.from_file("test.h5")

    lightcurve = grb["n1"]["lightcurve"]

    grbsave_to_gbm_fits("test.h5")

    files_to_remove = glob("*SynthGRB*.rsp")

    for f in files_to_remove:
        os.remove(f)
        
    files_to_remove = glob("*SynthGRB*.fits")

    for f in files_to_remove:
        os.remove(f)

    os.remove('test.h5')

    
def test_constant_grb(grb_constant):

    grb_constant.save('_bad.h5')
