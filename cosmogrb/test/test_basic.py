import os
import numpy as np
from glob import glob
from cosmogrb.grb import GBMGRB, GBMGRB_CPL
from cosmogrb.io.grb_save import GRBSave
from cosmogrb.io.gbm_fits import grbsave_to_gbm_fits

def test_gbm_constructor_and_plotting():

    grb = GBMGRB_CPL(
        ra=312.0,
        dec=-62.0,
        z=1.0,
        peak_flux=5e-9,
        alpha=-0.66,
        ep=500.0,
        tau=2.0,
        trise=0.1,
        duration=1.0,
        T0=0.1,
    )

    time = np.linspace(0, 20, 10)
    energy = np.logspace(1, 2, 10)

    grb.display_energy_dependent_light_curve(time, energy)
    grb.display_energy_integrated_light_curve(time)


def test_gbm_process():

    grb = GBMGRB_CPL(
        ra=312.0,
        dec=-62.0,
        z=1.0,
        peak_flux=5e-9,
        alpha=-0.66,
        ep=500.0,
        tau=2.0,
        trise=0.1,
        duration=1.0,
        T0=0.1,
    )

    grb.go(n_cores=1)

    files_to_remove = glob("SynthGRB*.rsp")

    for f in files_to_remove:
        os.remove(f)


def test_gbm_save():

    grb = GBMGRB_CPL(
        ra=312.0,
        dec=-62.0,
        z=1.0,
        peak_flux=5e-9,
        alpha=-0.66,
        ep=500.0,
        tau=2.0,
        trise=0.1,
        duration=1.0,
        T0=0.1,
    )

    grb.go(n_cores=1)

    grb.save("test.h5")

    files_to_remove = glob("SynthGRB*.rsp")

    for f in files_to_remove:
        os.remove(f)

def test_read_gbm_save():

    grb = GRBSave.from_file('test.h5')

    lightcurve = grb['n1']['lightcurve']
    


    grbsave_to_gbm_fits('test.h5')
