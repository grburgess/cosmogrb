from cosmogrb.grb import GRB
from cosmogrb.sampler.constant_cpl import ConstantCPL

import pytest

class DummyGRB(GRB):

    def __init__(self):

        super(DummyGRB, self).__init__(name='Dummy', source_function_class=ConstantCPL)

    
    def _setup(self):

        print("I do nothing")



def test_grb_constructor():

    # make sure we do not build stupid GRBs

    with pytest.raises(TypeError):

        grb = GRB()


    grb = DummyGRB()

    assert grb._name == 'Dummy'
    assert grb._T0 == 0
    assert grb._z == 1
    assert grb._ra == 0
    assert grb._dec == 0
    assert grb._duration == 1
