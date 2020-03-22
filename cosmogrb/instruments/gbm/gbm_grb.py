from cosmogrb.instruments.gbm.gbm_lightcurve import GBMLightCurve
from cosmogrb.instruments.gbm.gbm_background import GBMBackground
from cosmogrb.instruments.gbm.gbm_response import NaIResponse, BGOResponse
from cosmogrb.sampler.source import Source
from cosmogrb.sampler.cpl_source import CPLSourceFunction
from cosmogrb.sampler.constant_cpl import ConstantCPL


from cosmogrb.grb import GRB

import coloredlogs, logging
import cosmogrb.utils.logging

logger = logging.getLogger("cosmogrb.grb.gbmgrb")


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
        name="SynthGRB",
        duration=1,
        z=1,
        T0=0,
        ra=0,
        dec=0,
        **source_params
    ):

        
        self._use_plaw_sample = True


        


        # pass up
        super(GBMGRB, self).__init__(
            name=name, duration=duration, z=z, T0=T0, ra=ra, dec=dec,
            source_function_class=source_function_class, **source_params
        )

    def _setup_source(self):

        for key in self._responses.keys():

            source_function = self._source_function(
                response=self._responses[key], **self._source_params
            )

            source = Source(
                0.0,
                self._duration,
                source_function,
                use_plaw_sample=self._use_plaw_sample,
            )

            lc = GBMLightCurve(
                source,
                self._backgrounds[key],
                self._responses[key],
                name=key,
                grb_name=self._name,
                tstart=self._background_start,
                tstop=self._background_stop,
            )

            lc.set_time_adjustment(self._responses[key].T0)

            self._add_lightcurve(lc)

    def _setup(self):

        for det in self._gbm_detectors:
            if det[0] == "b":

                logger.debug(f"creating BGO reponse for {det} via grb {self._name}")

                rsp = BGOResponse(
                    det, self._ra, self._dec, self._T0, save=False, name=self._name
                )

            else:

                logger.debug(f"creating NAI reponse for {det} via GRB {self._name}")

                rsp = NaIResponse(
                    det, self._ra, self._dec, self._T0, save=False, name=self._name
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
    def __init__(
        self,
        ra,
        dec,
        z,
        peak_flux,
        alpha,
        ep,
        tau,
        trise,
        tdecay,
        duration,
        T0,
        name="SynthGRB",
    ):

        self._alpha = alpha
        self._ep = ep
        self._trise = trise

        source_params = dict(
            peak_flux=peak_flux,
            trise=trise,
            tdecay=tdecay,
            ep_tau=tau,
            alpha=alpha,
            ep_start=ep,
        )

        # pass up
        super(GBMGRB_CPL, self).__init__(
            source_function_class=CPLSourceFunction,
            name=name,
            duration=duration,
            z=z,
            T0=T0,
            ra=ra,
            dec=dec,
            **source_params
        )


class GBMGRB_CPL_Constant(GBMGRB):
    def __init__(
        self, ra, dec, z, peak_flux, alpha, ep, duration, T0, name="SynthGRB",
    ):

        source_params = dict(peak_flux=peak_flux, alpha=alpha, ep=ep,)

        # pass up
        super(GBMGRB_CPL_Constant, self).__init__(
            source_function_class=ConstantCPL,
            name=name,
            duration=duration,
            z=z,
            T0=T0,
            ra=ra,
            dec=dec,
            **source_params
        )
