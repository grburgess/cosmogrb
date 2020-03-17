from cosmogrb.config import cosmogrb_config

from cosmogrb.grb import GRB, GBMGRB, GBMGRB_CPL
from cosmogrb.io import GRBSave, grbsave_to_gbm_fits

__all__ = ["GRB", "GBMGRB", "GBMGRB_CPL", "GRBSave", "grbsave_to_gbm_fits"]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
