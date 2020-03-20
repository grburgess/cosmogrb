from cosmogrb.sampler.background import Background, BackgroundSpectrumTemplate
from cosmogrb.utils.file_utils import get_path_of_data_file

import os



_allowed_gbm_detectors = (
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


class GBMBackground(Background):
    def __init__(self, tstart, tstop, average_rate=1000, detector=None):

        assert (
            detector in _allowed_gbm_detectors
        ), "must use a proper GBM detector n<> or b<>"

        # get the GBM background spectral template

        detector_file = get_path_of_data_file(
            os.path.join("gbm_backgrounds", f"{detector}.h5")
        )

        # create a template

        background_spectrum_template = BackgroundSpectrumTemplate.from_file(
            detector_file, start_at_one=False
        )

        # call the super class

        super(GBMBackground, self).__init__(
            tstart=tstart,
            tstop=tstop,
            average_rate=average_rate,
            background_spectrum_template=background_spectrum_template,
        )
