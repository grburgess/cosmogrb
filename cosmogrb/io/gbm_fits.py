import numpy as np
from cosmogrb.io.grb_save import GRBSave
from cosmogrb.utils.tte_file import TTEFile


def grbsave_to_gbm_fits(file_name, destination="."):

    grb = GRBSave.from_file(file_name)

    for key in grb.keys:

        tstart = grb[key]["lightcurve"].tstart + grb[key]["lightcurve"].time_adjustment
        tstop = grb[key]["lightcurve"].tstop + grb[key]["lightcurve"].time_adjustment

        tte_file = TTEFile(
            det_name=key,
            tstart=tstart,
            tstop=tstop,
            trigger_time=grb.T0 + grb[key]["lightcurve"].time_adjustment,
            ra=grb.ra,
            dec=grb.dec,
            channel=np.arange(0, 128, dtype=np.int16),
            emin=grb[key]["response"].channel_edges[:-1],
            emax=grb[key]["response"].channel_edges[1:],
            pha=grb[key]["lightcurve"].pha.astype(np.int16),
            time=grb[key]["lightcurve"].times + grb[key]["lightcurve"].time_adjustment,
        )

        tte_file.writeto(f"tte_{grb.name}_{key}.fits", overwrite=True)

        rsp = grb[key]["response"]

        file_name = f"{rsp_grb.name}_{key}.rsp"

        rsp.to_fits(
            file_name, telescope_name="fermi", instrument_name=key, overwrite=True
        )
