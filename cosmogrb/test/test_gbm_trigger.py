import os
from glob import glob
from natsort import natsorted

from cosmogrb.instruments.gbm.process_gbm_universe import process_gbm_universe
from cosmogrb.utils.package_utils import get_path_of_data_dir, get_path_of_data_file
from cosmogrb.utils.file_utils import file_existing_and_readable
from cosmogrb.universe.survey import Survey
from cosmogrb.instruments.gbm.gbm_trigger import GBMTrigger


def test_gbm_trigger_constructor(gbm_trigger):

    assert not gbm_trigger.is_detected
    assert len(gbm_trigger.triggered_detectors) == 0
    assert len(gbm_trigger.triggered_times) == 0
    assert len(gbm_trigger.triggered_time_scales) == 0
    assert len(gbm_trigger._lc_names) == 12

    proper_order = [
        "n1",
        "n0",
        "n2",
        "n5",
        "n9",
        "n3",
        "n6",
        "na",
        "n7",
        "n4",
        "nb",
        "n8",
    ]

    for x, y in zip(gbm_trigger._lc_names, proper_order):
        assert x == y


def test_gbm_trigger_process(gbm_trigger):

    gbm_trigger.process()

    assert gbm_trigger.is_detected
    assert len(gbm_trigger.triggered_times) == 2
    assert len(gbm_trigger.triggered_time_scales) == 2
    assert len(gbm_trigger.triggered_detectors) == 2
    assert gbm_trigger.triggered_detectors[0] == "n1"
    assert gbm_trigger.triggered_detectors[1] == "n0"


def test_weak_gbm_trigger(weak_gbm_trigger):

    # make sure we do not trigger on weak
    # GRBs

    weak_gbm_trigger.process()

    assert not weak_gbm_trigger.is_detected


def test_process_survey(client, universe):

    # load the universe

    survey = Survey.from_file("universe.h5")


    for k,v in survey.items():

        v.grb.name == k

        assert v.detector_info is None

    # it should not be processed
    assert not survey.is_processed

    survey.info()
    
    survey.process(GBMTrigger, client=client)

    # now it should be processed
    assert survey.is_processed

    # save it
    survey.write("new_universe.h5")

    # see if we can load it
    survey2 = Survey.from_file("new_universe.h5")

    survey2.info()
    
    for k,v in survey2.items():
            
        v.grb.name == k

        v.detector_info.name == k


    
    # make  sure the loaded one is now processed
    assert survey2.is_processed

    files = glob("SynthGRB*store.h5")

    info_files = glob("SynthGRB*store_detection_info.h5")

    assert len(files) == len(info_files)

    for x, y in zip(natsorted(files), natsorted(info_files)):

        assert file_existing_and_readable(x)
        assert file_existing_and_readable(y)

        assert x.split("store")[0] == y.split("store")[0]

        os.remove(y)

    os.remove("new_universe.h5")
