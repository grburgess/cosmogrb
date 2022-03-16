import logging

from cosmogrb.grb import GRB, SourceParameter
from cosmogrb.instruments.gbm.gbm_background import GBMBackground
from cosmogrb.instruments.gbm.gbm_lightcurve import GBMLightCurve
from cosmogrb.instruments.gbm.gbm_orbit import gbm_orbit
from cosmogrb.instruments.gbm.gbm_response import BGOResponse, NaIResponse
from cosmogrb.sampler.constant_cpl import ConstantCPL
from cosmogrb.sampler.cpl_source import CPLSourceFunction
from cosmogrb.sampler.source import Source
from cosmogrb.utils.logging import setup_logger

logger = setup_logger(__name__)


class GBMGRB(GRB):

    _background_start = -100
    _background_stop = 300
    _gbm_detectors = (
        "n0",
        "n1",
        "n2",
        "n3",
        "n4",
        "n5",
        "n6",
        "n7",
        "n8",
        "n9",
        "na",
        "nb",
        "b0",
        "b1",
    )

    def __init__(
        self,
        source_function_class,
        **kwargs,
    ):

        self._use_plaw_sample = True

        # pass up
        super(GBMGRB, self).__init__(
            source_function_class=source_function_class,
            **kwargs,
        )

    def _setup_source(self):

        for key in self._responses.keys():

            source_function = self._source_function(
                response=self._responses[key], **self._source_params
            )

            source = Source(
                0.0,
                self.duration,
                source_function,
                z=self.z,
                use_plaw_sample=self._use_plaw_sample,
            )

            lc = GBMLightCurve(
                source,
                self._backgrounds[key],
                self._responses[key],
                name=key,
                grb_name=self.name,
                tstart=self._background_start,
                tstop=self._background_stop,
            )

            # we need to save the trigger time
            lc.set_time_adjustment(self._responses[key].trigger_time)

            self._add_lightcurve(lc)

    def _setup(self):

        for det in self._gbm_detectors:
            if det[0] == "b":

                logger.debug(
                    f"creating BGO reponse for {det} via grb {self.name}"
                )

                rsp = BGOResponse(
                    det, self.ra, self.dec, save=False, name=self.name
                )

            else:

                logger.debug(
                    f"creating NAI reponse for {det} via GRB {self.name}"
                )

                rsp = NaIResponse(
                    det, self.ra, self.dec, save=False, name=self.name
                )

            self._add_response(det, rsp)

            bkg = GBMBackground(
                self._background_start,
                self._background_stop,
                average_rate=500,
                detector=det,
            )

            self._add_background(det, bkg)

        self._setup_source()


class GBMGRB_CPL(GBMGRB):
    peak_flux = SourceParameter()
    alpha = SourceParameter()
    ep_start = SourceParameter()
    ep_tau = SourceParameter()
    trise = SourceParameter()
    tdecay = SourceParameter()

    def __init__(self, **kwargs):

        # pass up
        super(GBMGRB_CPL, self).__init__(
            source_function_class=CPLSourceFunction,
            **kwargs,
        )


class GBMGRB_CPL_Constant(GBMGRB):
    peak_flux = SourceParameter()
    alpha = SourceParameter()
    ep = SourceParameter()

    def __init__(self, **kwargs):

        # pass up
        super(GBMGRB_CPL_Constant, self).__init__(
            source_function_class=ConstantCPL,
            **kwargs,
        )
