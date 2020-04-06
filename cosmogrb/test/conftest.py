import os
import shutil
from glob import glob
import pytest

from cosmogrb.instruments.gbm import GBMGRB_CPL_Constant, GBMGRB, GBMGRB_CPL
from cosmogrb.utils.package_utils import get_path_of_data_file
from cosmogrb.instruments.gbm.gbm_universe import GBM_CPL_Universe
from cosmogrb.instruments.gbm.gbm_trigger import GBMTrigger

from dask.distributed import Client, LocalCluster

import popsynth


@pytest.fixture(scope="session")
def client():

    cluster = LocalCluster(n_workers=4)
    client = Client(cluster)

    yield client

    client.close()

    shutil.rmtree("dask-worker-space")


@pytest.fixture(scope="session")
def grb(client):
    grb = GBMGRB_CPL(
        ra=312.0,
        dec=-62.0,
        z=1.0,
        peak_flux=1e-5,
        alpha=-0.66,
        ep=500.0,
        tau=2.0,
        trise=0.1,
        tdecay=1.,
        duration=2.0,
        T0=0.1,
    )

    grb.go(client=client)

    grb.save("test_grb.h5")
    
    yield grb

    os.remove("test_grb.h5")


@pytest.fixture(scope="session")
def weak_grb(client):
    grb = GBMGRB_CPL(
        ra=312.0,
        dec=-62.0,
        z=1.0,
        peak_flux=5e-20,
        alpha=-0.66,
        ep=500.0,
        tau=2.0,
        trise=0.1,
        tdecay=0.5,
        duration=1.0,
        T0=0.1,
    )

    grb.go(client=client)

    grb.save("weak_grb.h5")

    yield grb

    os.remove("weak_grb.h5")


@pytest.fixture(scope="session")
def grb_constant(client):
    grb = GBMGRB_CPL_Constant(
        ra=312.0,
        dec=-62.0,
        z=1.0,
        peak_flux=5e-9,
        alpha=-0.66,
        ep=500.0,
        duration=1.0,
        T0=0.1,
    )

    grb.go(client=client)

    return grb


@pytest.fixture(scope="session")
def universe(client):
    population_file = get_path_of_data_file("test_grb_pop.h5")

    universe = GBM_CPL_Universe(population_file)

    universe.go(client)
    universe.save("universe.h5")

    yield universe

    files_to_remove = glob("SynthGRB*store.h5")

    for f in files_to_remove:
        os.remove(f)

    os.remove("universe.h5")


@pytest.fixture(scope="session")
def gbm_trigger(grb):

    gbm_trigger = GBMTrigger("test_grb.h5")

    return gbm_trigger


@pytest.fixture(scope="session")
def weak_gbm_trigger(weak_grb):

    # a weak GRB that should not trigger a detection
    weak_gbm_trigger = GBMTrigger("weak_grb.h5", max_n_dets=4)

    return weak_gbm_trigger
