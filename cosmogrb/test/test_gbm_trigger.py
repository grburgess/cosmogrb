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

    gbm_trigger.process_triggers()

    assert gbm_trigger.is_detected
    assert len(gbm_trigger.triggered_times) == 2
    assert len(gbm_trigger.triggered_time_scales) == 2
    assert len(gbm_trigger.triggered_detectors) == 2
    assert gbm_trigger.triggered_detectors[0] == "n1"
    assert gbm_trigger.triggered_detectors[1] == "n0"


def test_weak_gbm_trigger(weak_gbm_trigger):

    # make sure we do not trigger on weak
    # GRBs

    weak_gbm_trigger.process_triggers()

    assert not weak_gbm_trigger.is_detected
