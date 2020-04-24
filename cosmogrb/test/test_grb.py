from cosmogrb.grb import GRB, SourceParameter
from cosmogrb.sampler.constant_cpl import ConstantCPL

import pytest


class DummyGRB(GRB):
    def __init__(self, **kwargs):

        super(DummyGRB, self).__init__(**kwargs, source_function_class=ConstantCPL)

    def _setup(self):

        print("I do nothing")


class ChildDummyGRB(DummyGRB):

    x = SourceParameter(default=0, vmin=-1, vmax=1)

    def __init__(self, **kwargs):

        super(ChildDummyGRB, self).__init__(**kwargs)


def test_grb_constructor():

    # make sure we do not build stupid GRBs

    with pytest.raises(TypeError):

        grb = GRB()

    grb = DummyGRB()

    assert grb._source_params == {}

    for rp in ["name", "T0", "z", "ra", "dec", "duration"]:

        assert rp in GRB._required_names

    for rp in ["name", "T0", "z", "ra", "dec", "duration"]:

        assert rp in DummyGRB._required_names

    assert grb.name == "SynthGRB"
    assert grb.T0 == 0
    assert grb.z == 1
    assert grb.ra == 0
    assert grb.dec == 0
    assert grb.duration == 1

    grb = DummyGRB(name="AnotherDummy")

    assert grb.name == "AnotherDummy"
    assert grb.T0 == 0
    assert grb.z == 1
    assert grb.ra == 0
    assert grb.dec == 0
    assert grb.duration == 1

    kwargs = dict(name="name", T0=10, z=4, ra=10, dec=4, duration=3.0)

    grb = DummyGRB(**kwargs)

    assert grb.name == "name"
    assert grb.T0 == 10
    assert grb.z == 4
    assert grb.ra == 10
    assert grb.dec == 4
    assert grb.duration == 3

    # test setting outside limits

    with pytest.raises(AssertionError):
        grb = DummyGRB(z=-1)

    grb = DummyGRB()

    with pytest.raises(AssertionError):
        grb.z = -10

    with pytest.raises(AssertionError):
        grb.z = 1000


def test_inhereted_grb():

    grb = ChildDummyGRB()

    assert grb._source_params == {}

    assert "x" in ChildDummyGRB._parameter_names

    for rp in ["name", "T0", "z", "ra", "dec", "duration"]:

        assert rp in ChildDummyGRB._required_names

    assert grb.name == "SynthGRB"
    assert grb.T0 == 0
    assert grb.z == 1
    assert grb.ra == 0
    assert grb.dec == 0
    assert grb.duration == 1
    assert grb.x == 0

    grb = ChildDummyGRB(name="AnotherDummy", x=0.5)

    assert grb.name == "AnotherDummy"
    assert grb.T0 == 0
    assert grb.z == 1
    assert grb.ra == 0
    assert grb.dec == 0
    assert grb.duration == 1
    assert grb.x == 0.5

    kwargs = dict(name="name", T0=10, z=4, ra=10, dec=4, duration=3.0, x=-0.2)

    grb = ChildDummyGRB(**kwargs)

    assert grb.name == "name"
    assert grb.T0 == 10
    assert grb.z == 4
    assert grb.ra == 10
    assert grb.dec == 4
    assert grb.duration == 3
    assert grb.x == -0.2

    # test setting outside limits

    with pytest.raises(AssertionError):
        grb = ChildDummyGRB(z=-1)

    grb = ChildDummyGRB()

    with pytest.raises(AssertionError):
        grb.z = -10

    with pytest.raises(AssertionError):
        grb.z = 1000

    with pytest.raises(AssertionError):
        grb = ChildDummyGRB(x=-10)

    grb = ChildDummyGRB()

    with pytest.raises(AssertionError):
        grb.x = -10

    with pytest.raises(AssertionError):
        grb.x = 1000
