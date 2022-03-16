import astropy.units as u
import numpy as np

from cosmogrb.utils.fits_file import FITSExtension, FITSFile


# lifted from 3ML
class EBOUNDS(FITSExtension):

    _HEADER_KEYWORDS = (
        ("EXTNAME", "EBOUNDS", "Extension name"),
        ("HDUCLASS", "OGIP    ", "format conforms to OGIP standard"),
        (
            "HDUVERS",
            "1.1.0   ",
            "Version of format (OGIP memo CAL/GEN/92-002a)",
        ),
        (
            "HDUDOC",
            "OGIP memos CAL/GEN/92-002 & 92-002a",
            "Documents describing the forma",
        ),
        (
            "HDUVERS1",
            "1.0.0   ",
            "Obsolete - included for backwards compatibility",
        ),
        (
            "HDUVERS2",
            "1.1.0   ",
            "Obsolete - included for backwards compatibility",
        ),
        ("CHANTYPE", "PI", "Channel type"),
        ("CONTENT", "OGIPResponse Matrix", "File content"),
        ("HDUCLAS1", "RESPONSE", "Extension contains response data  "),
        ("HDUCLAS2", "EBOUNDS ", "Extension contains EBOUNDS"),
        ("TLMIN1", 1, "Minimum legal channel number"),
    )

    def __init__(self, energy_boundaries):
        """
        Represents the EBOUNDS extension of a response matrix FITS file
        :param energy_boundaries: lower bound of channel energies (in keV)
        """

        n_channels = len(energy_boundaries) - 1

        data_tuple = (
            ("CHANNEL", range(1, n_channels + 1)),
            ("E_MIN", energy_boundaries[:-1] * u.keV),
            ("E_MAX", energy_boundaries[1:] * u.keV),
        )

        super(EBOUNDS, self).__init__(data_tuple, self._HEADER_KEYWORDS)


class MATRIX(FITSExtension):
    """
    Represents the MATRIX extension of a response FITS file following the OGIP format
    :param mc_energies_lo: lower bound of MC energies (in keV)
    :param mc_energies_hi: hi bound of MC energies (in keV)
    :param channel_energies_lo: lower bound of channel energies (in keV)
    :param channel_energies_hi: hi bound of channel energies (in keV
    :param matrix: the redistribution matrix, representing energy dispersion effects
    """

    _HEADER_KEYWORDS = [
        ("EXTNAME", "MATRIX", "Extension name"),
        ("HDUCLASS", "OGIP    ", "format conforms to OGIP standard"),
        (
            "HDUVERS",
            "1.1.0   ",
            "Version of format (OGIP memo CAL/GEN/92-002a)",
        ),
        (
            "HDUDOC",
            "OGIP memos CAL/GEN/92-002 & 92-002a",
            "Documents describing the forma",
        ),
        (
            "HDUVERS1",
            "1.0.0   ",
            "Obsolete - included for backwards compatibility",
        ),
        (
            "HDUVERS2",
            "1.1.0   ",
            "Obsolete - included for backwards compatibility",
        ),
        ("HDUCLAS1", "RESPONSE", "dataset relates to spectral response"),
        ("HDUCLAS2", "RSP_MATRIX", "dataset is a spectral response matrix"),
        ("HDUCLAS3", "REDIST", "dataset represents energy dispersion only"),
        ("CHANTYPE", "PI ", "Detector Channel Type in use (PHA or PI)"),
        ("DETCHANS", None, "Number of channels"),
        ("FILTER", "", "Filter used"),
        ("TLMIN4", 1, "Minimum legal channel number"),
    ]

    def __init__(self, mc_energies, channel_energies, matrix):

        n_mc_channels = len(mc_energies) - 1
        n_channels = len(channel_energies) - 1

        assert matrix.shape == (
            n_channels,
            n_mc_channels,
        ), "Matrix has the wrong shape. Should be %i x %i, got %i x %i" % (
            n_channels,
            n_mc_channels,
            matrix.shape[0],
            matrix.shape[1],
        )

        ones = np.ones(n_mc_channels, np.int16)

        # We need to format the matrix as a list of n_mc_channels rows of n_channels length

        data_tuple = (
            ("ENERG_LO", mc_energies[:-1] * u.keV),
            ("ENERG_HI", mc_energies[1:] * u.keV),
            ("N_GRP", ones),
            ("F_CHAN", ones),
            ("N_CHAN", np.ones(n_mc_channels, np.int16) * n_channels),
            ("MATRIX", matrix.T),
        )

        super(MATRIX, self).__init__(data_tuple, self._HEADER_KEYWORDS)

        # Update DETCHANS
        self.hdu.header.set("DETCHANS", n_channels)


class SPECRESP_MATRIX(MATRIX):
    """
    Represents the SPECRESP_MATRIX extension of a response FITS file following the OGIP format
    :param mc_energies_lo: lower bound of MC energies (in keV)
    :param mc_energies_hi: hi bound of MC energies (in keV)
    :param channel_energies_lo: lower bound of channel energies (in keV)
    :param channel_energies_hi: hi bound of channel energies (in keV
    :param matrix: the redistribution matrix, representing energy dispersion effects and effective area information
    """

    def __init__(self, mc_energies, channel_energies, matrix):

        # This is essentially exactly the same as MATRIX, but with a different extension name

        super(SPECRESP_MATRIX, self).__init__(
            mc_energies, channel_energies, matrix
        )

        # Change the extension name
        self.hdu.header.set("EXTNAME", "SPECRESP MATRIX")
        self.hdu.header.set("HDUCLAS3", "FULL")


class RMF(FITSFile):
    """
    A RMF file, the OGIP format for a matrix representing energy dispersion effects.
    """

    def __init__(
        self, mc_energies, ebounds, matrix, telescope_name, instrument_name
    ):

        # Make sure that the provided iterables are of the right type for the FITS format

        mc_energies = np.array(mc_energies, np.float32)

        ebounds = np.array(ebounds, np.float32)

        # Create EBOUNDS extension
        ebounds_ext = EBOUNDS(ebounds)

        # Create MATRIX extension
        matrix_ext = MATRIX(mc_energies, ebounds, matrix)

        # Set telescope and instrument name
        matrix.hdu.header.set("TELESCOP", telescope_name)
        matrix.hdu.header.set("INSTRUME", instrument_name)

        # Create FITS file
        super(RMF, self).__init__(fits_extensions=[ebounds_ext, matrix_ext])


class RSP(FITSFile):
    """
    A response file, the OGIP format for a matrix representing both energy dispersion effects and effective area,
    in the same matrix.
    """

    def __init__(
        self, mc_energies, ebounds, matrix, telescope_name, instrument_name
    ):

        # Make sure that the provided iterables are of the right type for the FITS format

        mc_energies = np.array(mc_energies, np.float32)

        ebounds = np.array(ebounds, np.float32)

        # Create EBOUNDS extension
        ebounds_ext = EBOUNDS(ebounds)

        # Create MATRIX extension
        matrix_ext = SPECRESP_MATRIX(mc_energies, ebounds, matrix)

        # Set telescope and instrument name
        matrix_ext.hdu.header.set("TELESCOP", telescope_name)
        matrix_ext.hdu.header.set("INSTRUME", instrument_name)

        # Create FITS file
        super(RSP, self).__init__(fits_extensions=[ebounds_ext, matrix_ext])
