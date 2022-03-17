from cosmogrb.config import cosmogrb_config
from cosmogrb.io import GRBSave, grbsave_to_gbm_fits
import cosmogrb.instruments.gbm as gbm


__all__ = ["gbm", "GRBSave", "grbsave_to_gbm_fits", "cosmogrb_config"]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
