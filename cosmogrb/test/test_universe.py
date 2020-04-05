from glob import glob
import popsynth
import pytest

from cosmogrb.utils.file_utils import file_existing_and_readable


def test_gbm_universe(universe):

    assert file_existing_and_readable("universe.h5")
    assert universe._save_path == "."
    assert universe._grb_base_name == "SynthGRB"
    assert universe._is_processed


def test_gbm_universe_serial(universe):

    universe.go(client=None)
