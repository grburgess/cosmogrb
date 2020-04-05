import os

import numpy as np
from glob import glob

# from cosmogrb.instruments.gbm import GBMGRB_CPL_Constant, GBMGRB, GBMGRB_CPL

from cosmogrb.io.grb_save import GRBSave
from cosmogrb.io.gbm_fits import grbsave_to_gbm_fits
from cosmogrb.utils.package_utils import get_path_of_data_file

import pytest


def test_gbm_constructor_and_plotting(grb):

    time = np.linspace(0, 20, 10)
    energy = np.logspace(1, 2, 10)

    grb.display_energy_dependent_light_curve(time, energy)
    grb.display_energy_integrated_light_curve(time)

    print(grb)
    grb.info()


def test_gbm_save(grb):

    file_name = "test.h5"

    grb.save(file_name)

    os.remove(file_name)


def test_read_gbm_save():

    path = get_path_of_data_file("SynthGRB_0_store.h5")

    grb = GRBSave.from_file(path)

    print(grb)
    grb.info()

    lightcurve = grb["n1"]["lightcurve"]

    print(lightcurve)
    lightcurve.info()

    grbsave_to_gbm_fits(path)

    files_to_remove = glob("*SynthGRB*.rsp")

    for f in files_to_remove:
        os.remove(f)

    files_to_remove = glob("*SynthGRB*.fits")

    for f in files_to_remove:
        os.remove(f)


def test_constant_grb(grb_constant):

    file_name = "_cpl_const.h5"

    grb_constant.save(file_name)

    os.remove(file_name)
