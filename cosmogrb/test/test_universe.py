from glob import glob

import popsynth
import pytest


def test_gbm_universe(universe, client):

    universe.go(client)
    universe.save('universe.h5')
    

def test_gbm_universe_serial(universe):

    universe.go(client=None)
