from cosmogrb.utils.package_utils import get_path_of_data_file
from cosmogrb.io.grb_save import GRBSave


def test_lightcurve_plotting():

    grb = GRBSave.from_file(get_path_of_data_file("grb.h5"))

    for key in grb.keys:

        lc = grb[key]["lightcurve"]

        lc.display_lightcurve()
        lc.display_background()
        lc.display_source()
