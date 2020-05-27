import os

import numpy as np

from cosmogrb.io.grb_save import GRBSave
from cosmogrb.utils.tte_file import TTEFile


def grbsave_to_gbm_fits(file_name, destination=".", detectors=None):

    if isinstance(file_name, GRBSave):

        grb = file_name

    else:

        grb = GRBSave.from_file(file_name)

    files = {}

    # set up the detector filter

    if detectors is None:

        detectors = list(grb.keys())

    else:

        for det in detectors:

            assert det in grb, f"{det} is not a in the light curve list"

    for key, det in grb.items():

        if key in detectors:

            tstart = det["lightcurve"].tstart + \
                det["lightcurve"].time_adjustment
            tstop = det["lightcurve"].tstop + det["lightcurve"].time_adjustment

            tte_file = TTEFile(
                det_name=key,
                tstart=tstart,
                tstop=tstop,
                trigger_time=grb.T0 + det["lightcurve"].time_adjustment,
                ra=grb.ra,
                dec=grb.dec,
                channel=np.arange(0, 128, dtype=np.int16),
                emin=det["response"].channel_edges[:-1],
                emax=det["response"].channel_edges[1:],
                pha=det["lightcurve"].pha.astype(np.int16),
                time=det["lightcurve"].times +
                det["lightcurve"].time_adjustment,
            )

            tte_file_name = os.path.join(
                destination, f"tte_{grb.name}_{key}.fits")

            tte_file.writeto(tte_file_name, overwrite=True)

            rsp = det["response"]

            rsp_file_name = os.path.join(
                destination, f"rsp_{grb.name}_{key}.rsp")

            rsp.to_fits(
                rsp_file_name, telescope_name="fermi", instrument_name=key, overwrite=True
            )

            sub_dict = {}

            sub_dict["tte"] = tte_file_name
            sub_dict["rsp"] = rsp_file_name

            files[key] = sub_dict

    return files
