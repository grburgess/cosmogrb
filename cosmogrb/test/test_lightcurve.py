from cosmogrb.utils.package_utils import get_path_of_data_file
from cosmogrb.io.grb_save import GRBSave


def test_lightcurve_plotting(grb):

    grb = GRBSave.from_file("test_grb.h5")

    for key, get in grb.items():

        lc = grb[key]["lightcurve"]

        lc.display_lightcurve()
        lc.display_background()
        lc.display_source()

        lc.display_lightcurve(emin=100)
        lc.display_background(emin=100)
        lc.display_source(emin=100)

        lc.display_lightcurve(emax=100)
        lc.display_background(emax=100)
        lc.display_source(emax=100)

        lc.display_lightcurve(emin=100, emax=1000)
        lc.display_background(emin=100, emax=1000)
        lc.display_source(emin=100, emax=1000)

        lc.display_count_spectrum()
        lc.display_count_spectrum_background()
        lc.display_count_spectrum_source()

        lc.display_count_spectrum(tmin=0)
        lc.display_count_spectrum_background(tmin=0)
        lc.display_count_spectrum_source(tmin=0)

        lc.display_count_spectrum(tmax=10)
        lc.display_count_spectrum_background(tmax=10)
        lc.display_count_spectrum_source(tmax=10)

        lc.display_count_spectrum(tmin=0, tmax=10)
        lc.display_count_spectrum_background(tmin=0, tmax=10)
        lc.display_count_spectrum_source(tmin=0, tmax=10)
