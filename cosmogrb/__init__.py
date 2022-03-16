from cosmogrb.config import cosmogrb_config
import cosmogrb.instruments.gbm as gbm
from cosmogrb.io import GRBSave, grbsave_to_gbm_fits

__all__ = ["gbm", "GRBSave", "grbsave_to_gbm_fits"]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
