import numpy as np
from cosmogrb.io.grb_save import GRBSave
from cosmogrb.utils.tte_file import TTEFile


def grbsave_to_gbm_fits(file_name, destination="."):

    grb = GRBSave.from_file(file_name)

    for key, det in grb.items():

        tstart = det["lightcurve"].tstart + det["lightcurve"].time_adjustment
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
            time=det["lightcurve"].times + det["lightcurve"].time_adjustment,
        )

        tte_file.writeto(f"tte_{grb.name}_{key}.fits", overwrite=True)

        rsp = det["response"]

        file_name = f"rsp_{grb.name}_{key}.rsp"

        rsp.to_fits(
            file_name, telescope_name="fermi", instrument_name=key, overwrite=True
        )
