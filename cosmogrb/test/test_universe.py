from cosmogrb.universe.gbm_universe import GBM_CPL_Universe
from cosmogrb.utils.package_utils import get_path_of_data_file

from dask.distributed import Client, LocalCluster

import popsynth

def test_gbm_universe():

    cluster = LocalCluster(n_workers=2)

    client = Client(cluster)
    
    population_file = get_path_of_data_file('test_grb_pop.h5')

    pop = popsynth.Population.from_file(population_file)

    uni = GBM_CPL_Universe(pop)
    
    uni.go(client)


def test_gbm_universe_serial():
    
    population_file = get_path_of_data_file('test_grb_pop.h5')

    pop = popsynth.Population.from_file(population_file)

    uni = GBM_CPL_Universe(pop)
    
    uni.go(client=None)