from cosmogrb.instruments.gbm import GBMBackground


allowed_dets = (
    "n0",
    "n1",
    "n2",
    "n3",
    "n4",
    "n5",
    "n6",
    "n7",
    "n8",
    "n9",
    "na",
    "nb",
    "b1",
    "b0",
)


def test_gbm_background_constructor():

    for det in allowed_dets:

        bkg = GBMBackground(-10, 10, average_rate=100.0, detector=det)
