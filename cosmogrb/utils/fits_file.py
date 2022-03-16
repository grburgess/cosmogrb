import pkg_resources
from responsum.utils.fits_file import FITSExtension as FE
from responsum.utils.fits_file import FITSFile


class FITSExtension(FE):

    # I use __new__ instead of __init__ because I need to use the classmethod .from_columns instead of the
    # constructor of fits.BinTableHDU

    def __init__(self, data_tuple, header_tuple):

        creator = "COSMOGRB v.%s" % (
            pkg_resources.get_distribution("cosmogrb").version
        )

        super(FITSExtension, self).__init__(
            data_tuple, header_tuple, creator=creator
        )
