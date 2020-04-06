import time
import popsynth

from cosmogrb.instruments.gbm import GBM_CPL_Universe

from dask.distributed import Client, LocalCluster


# this is a script that is used to generate the test data for the
# pytest. it is meant to be run from the top of the pacakge

