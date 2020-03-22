
import popsynth
import pytest




    
    

def test_gbm_universe(universe, client):

    universe.go(client)


def test_gbm_universe_serial(universe):

    universe.go(client=None)
