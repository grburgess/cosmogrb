import time
import popsynth

from cosmogrb.instruments.gbm import GBM_CPL_Universe

from dask.distributed import Client, LocalCluster


# this is a script that is used to generate the test data for the
# pytest. it is meant to be run from the top of the pacakge


pop = popsynth.Population.from_file("cosmogrb/data/test_grb_pop.h5")

uni = GBM_CPL_Universe(pop, save_path="cosmogrb/data/")

uni.go(client=None)
