import astropy.io.fits as fits
import astropy.units as astropy_units
import numpy as np

from .fits_file import FITSExtension, FITSFile

_det_translate = dict(
    n0="NAI_00",
    n1="NAI_01",
    n2="NAI_02",
    n3="NAI_03",
    n4="NAI_04",
    n5="NAI_05",
    n6="NAI_06",
    n7="NAI_07",
    n8="NAI_08",
    n9="NAI_09",
    na="NAI_10",
    nb="NAI_11",
    b0="BGO_00",
    b1="BGO_01",
)


class EBOUNDS(FITSExtension):
    _HEADER_KEYWORDS = (
        ("EXTNAME", "EBOUNDS", "Extension name"),
        ("CONTENT", "OGIP PHA data", "File content"),
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
        ("HDUCLAS1", "RESPONSE", "These are typically found in RMF files  "),
        ("HDUCLAS2", "EBOUNDS ", "Fram CAL/GEN/92-002"),
        ("FILTER", "", "Filter used"),
        ("CHANTYPE", "PHA", "Channel type"),
        ("DETCHANS", 128, "Number of channels"),
        ("TELESCOP", "GLAST", "Name of mission/satelite"),
        ("INSTRUME", "GBM", "Specific instrument used for observation"),
        ("DATE", "2009-05-19T18:49:32", "file creation date"),
        ("DATE-OBS", "2009-05-19T18:49:32", "Date of start of observation"),
        ("DATE-END", "2009-05-19T18:49:32", "Date of end of observation"),
        ("OBSERVER", "God", "The creator of the Universe"),
        ("OBJECT", "GRB080916200", "Burst name in standard format"),
        ("ORIGIN", "MPE", "Name of organization creating the file"),
        ("TIMESYS", "TT", "Time system used in keywords"),
        ("TIMEUNIT", "s", "Time since MJDREF, used in TSTART and TSTOP"),
        ("MJDREFI", 51910, "MJD of GLAST reference epoch"),
        ("MJDREFI", 7.428703703703703e-4, "MJD of GLAST reference epoch"),
        ("RADECSYS", "FK5     ", "Stellar reference frame"),
        ("EQUINOX", 2000.0, "Equinox of RA and Dec"),
        ("RA_OBJ", None, "Calculated RA of burst"),
        ("DEC_OBJ", None, "Calculated Dec of burst"),
        ("ERR_RAD", 3.000, "Calculated Location of Error Radius"),
        ("EXTVER", 1, ""),
        ("CH2E_VER", "SPLINE 2.0", ""),
        ("GAIN_COR", 1.0, ""),
        ("TSTART", None, "[GLAST MET] Observation start time"),
        ("TSTOP", None, "[GLAST MET] Observation stop time"),
        ("TRIGTIME", None, "Trigger time realtive to MJDREF, double precision"),
        ("DETNAM", None, "Individual detector name"),
    )

    def __init__(
        self,
        det_name,
        tstart,
        tstop,
        trigger_time,
        ra,
        dec,
        channel,
        emin,
        emax,
    ):

        data_list = [
            ("CHANNEL", channel),
            ("E_MIN", emin * astropy_units.keV),
            ("E_MAX", emax * astropy_units.keV),
        ]

        super(EBOUNDS, self).__init__(tuple(data_list), self._HEADER_KEYWORDS)

        self.hdu.header.set("RA_OBJ", ra)
        self.hdu.header.set("DEC_OBJ", dec)
        self.hdu.header.set("TSTART", tstart)
        self.hdu.header.set("TSTOP", tstop)
        self.hdu.header.set("TRIGTIME", trigger_time)
        self.hdu.header.set("DETNAM", _det_translate[det_name])


class EVENTS(FITSExtension):
    _HEADER_KEYWORDS = (
        ("EXTNAME", "EVENTS", "Extension name"),
        ("CONTENT", "OGIP PHA data", "File content"),
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
        ("HDUCLAS1", "EVENTS", "Extension constains events  "),
        ("FILTER", "", "Filter used"),
        ("DETCHANS", 128, "Number of channels"),
        ("TELESCOP", "GLAST", "Name of mission/satelite"),
        ("INSTRUME", "GBM", "Specific instrument used for observation"),
        ("DATE", "2009-05-19T18:49:32", "file creation date"),
        ("DATE-OBS", "2009-05-19T18:49:32", "Date of start of observation"),
        ("DATE-END", "2009-05-19T18:49:32", "Date of end of observation"),
        ("OBSERVER", "God", "The creator of the Universe"),
        ("OBJECT", "GRB080916200", "Burst name in standard format"),
        ("ORIGIN", "MPE", "Name of organization creating the file"),
        ("TIMESYS", "TT", "Time system used in keywords"),
        ("TIMEUNIT", "s", "Time since MJDREF, used in TSTART and TSTOP"),
        ("MJDREFI", 51910, "MJD of GLAST reference epoch"),
        ("MJDREFI", 7.428703703703703e-4, "MJD of GLAST reference epoch"),
        ("RADECSYS", "FK5     ", "Stellar reference frame"),
        ("EQUINOX", 2000.0, "Equinox of RA and Dec"),
        ("RA_OBJ", None, "Calculated RA of burst"),
        ("DEC_OBJ", None, "Calculated Dec of burst"),
        ("ERR_RAD", 3.000, "Calculated Location of Error Radius"),
        ("EXTVER", 1, ""),
        ("CH2E_VER", "SPLINE 2.0", ""),
        ("GAIN_COR", 1.0, ""),
        ("TSTART", None, "[GLAST MET] Observation start time"),
        ("TSTOP", None, "[GLAST MET] Observation stop time"),
        ("TRIGTIME", None, "Trigger time realtive to MJDREF, double precision"),
        # ("TZERO1", None, "Time offset"),
        ("FIFO_END", None, "Time of the last event in FIFO"),
        ("PRMT_BEG", None, "Time of the first event in prompt"),
        ("DETNAM", None, "Individual detector name"),
    )

    def __init__(
        self, det_name, tstart, tstop, trigger_time, ra, dec, pha, time
    ):

        data_list = [("TIME", time * astropy_units.s), ("PHA", pha)]

        super(EVENTS, self).__init__(tuple(data_list), self._HEADER_KEYWORDS)

        self.hdu.header.set("RA_OBJ", ra)
        self.hdu.header.set("DEC_OBJ", dec)
        self.hdu.header.set("TSTART", tstart)
        self.hdu.header.set("TSTOP", tstop)
        self.hdu.header.set("TRIGTIME", trigger_time)
        # self.hdu.header.set("TZERO1", trigger_time)
        self.hdu.header.set("PRMT_BEG", trigger_time)
        self.hdu.header.set("FIFO_END", tstop)
        self.hdu.header.set("DETNAM", _det_translate[det_name])


class GTI(FITSExtension):

    _HEADER_KEYWORDS = (
        ("EXTNAME", "GTI", "Extension name"),
        ("CONTENT", "OGIP PHA data", "File content"),
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
        ("HDUCLAS1", "GTI", "Extension constains events  "),
        ("FILTER", "", "Filter used"),
        ("TELESCOP", "GLAST", "Name of mission/satelite"),
        ("INSTRUME", "GBM", "Specific instrument used for observation"),
        ("DATE", "2009-05-19T18:49:32", "file creation date"),
        ("DATE-OBS", "2009-05-19T18:49:32", "Date of start of observation"),
        ("DATE-END", "2009-05-19T18:49:32", "Date of end of observation"),
        ("OBSERVER", "God", "The creator of the Universe"),
        ("OBJECT", "GRB080916200", "Burst name in standard format"),
        ("ORIGIN", "MPE", "Name of organization creating the file"),
        ("TIMESYS", "TT", "Time system used in keywords"),
        ("TIMEUNIT", "s", "Time since MJDREF, used in TSTART and TSTOP"),
        ("MJDREFI", 51910, "MJD of GLAST reference epoch"),
        ("MJDREFI", 7.428703703703703e-4, "MJD of GLAST reference epoch"),
        ("RADECSYS", "FK5     ", "Stellar reference frame"),
        ("EQUINOX", 2000.0, "Equinox of RA and Dec"),
        ("RA_OBJ", None, "Calculated RA of burst"),
        ("DEC_OBJ", None, "Calculated Dec of burst"),
        ("ERR_RAD", 3.000, "Calculated Location of Error Radius"),
        ("EXTVER", 1, ""),
        ("CH2E_VER", "SPLINE 2.0", ""),
        ("GAIN_COR", 1.0, ""),
        ("TSTART", None, "[GLAST MET] Observation start time"),
        ("TSTOP", None, "[GLAST MET] Observation stop time"),
        ("TRIGTIME", None, "Trigger time realtive to MJDREF, double precision"),
        # ("TZERO1", None, "Time offset"),
        ("DETNAM", None, "Individual detector name"),
    )

    def __init__(self, det_name, tstart, tstop, trigger_time, ra, dec):

        data_list = [("START", np.array([tstart])), ("STOP", np.array([tstop]))]

        super(GTI, self).__init__(tuple(data_list), self._HEADER_KEYWORDS)

        self.hdu.header.set("RA_OBJ", ra)
        self.hdu.header.set("DEC_OBJ", dec)
        self.hdu.header.set("TSTART", tstart)
        self.hdu.header.set("TSTOP", tstop)
        self.hdu.header.set("TRIGTIME", trigger_time)

        # self.hdu.header.set("TZERO1", trigger_time)
        self.hdu.header.set("DETNAM", _det_translate[det_name])


class TTEFile(FITSFile):
    def __init__(
        self,
        det_name,
        tstart,
        tstop,
        trigger_time,
        ra,
        dec,
        channel,
        emin,
        emax,
        pha,
        time,
    ):

        # just to find the info
        primary = fits.PrimaryHDU()

        primary.header.set("TSTART", tstart)
        primary.header.set("TSTOP", tstop)
        primary.header.set("TRIGTIME", trigger_time)
        primary.header.set("DATE-OBS", "2009-05-19T18:49:32")
        primary.header.set("DATE-END", "2009-05-19T18:49:32")
        primary.header.set("DETNAM", det_name)
        primary.header.set("INSTRUME", "GBM")
        primary.header.set("TELESCOP", "GLAST")

        ebounds_extension = EBOUNDS(
            det_name, tstart, tstop, trigger_time, ra, dec, channel, emin, emax
        )

        events_extension = EVENTS(
            det_name=det_name,
            tstart=tstart,
            tstop=tstop,
            trigger_time=trigger_time,
            ra=ra,
            dec=dec,
            pha=pha,
            time=time,
        )

        gti_extension = GTI(det_name, tstart, tstop, trigger_time, ra, dec)

        super(TTEFile, self).__init__(
            primary_hdu=primary,
            fits_extensions=[
                ebounds_extension,
                events_extension,
                gti_extension,
            ],
        )
