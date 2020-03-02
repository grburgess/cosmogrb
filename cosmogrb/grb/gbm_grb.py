from cosmogrb.lightcurve import GBMLightCurve
from cosmogrb.sampler.source import Source
from cosmogrb.sampler.background import GBMBackground
from cosmogrb.sampler.cpl_source import CPLSourceFunction
from cosmogrb.sampler.constant_cpl import ConstantCPL
from cosmogrb.response import NaIResponse, BGOResponse
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
        ra,
        dec,
        z,
        duration,
        T0,
        source_function_class,
        name="SynthGRB",
        **source_function_params,    
    ):

        # pass up
        super(GBMGRB, self).__init__(
            name=name, duration=duration, z=z, T0=T0, ra=ra, dec=dec
        )

        for det in self._gbm_detectors:
            if det[0] == "b":

                logger.debug(f"creating BGO reponse for {det} via grb {name}")

                rsp = BGOResponse(det, ra, dec, T0, save=True, name=name)

            else:

                logger.debug(f"creating NAI reponse for {det} via GRB {name}")

                rsp = NaIResponse(det, ra, dec, T0, save=True, name=name)

            bkg = GBMBackground(
                self._background_start,
                self._background_stop,
                average_rate=500,
                detector=det,
            )

            source_function = source_function_class(rsp=rsp, **source_function_params)
  
            source = Source(0.0, duration, source_function, use_plaw_sample=True)

            self._add_lightcurve(
                GBMLightCurve(source, bkg, rsp, name=det, grb_name=self._name)
            )

class GBMGRB_CPL(GRB):

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
        ra,
        dec,
        z,
        peak_flux,
        alpha,
        ep,
        tau,
        trise,
        duration,
        T0,
        name="SynthGRB",
    ):

        self._alpha = alpha
        self._ep = ep
        self._trise = trise

        # pass up
        super(GBMGRB, self).__init__(
            name=name, duration=duration, z=z, T0=T0, ra=ra, dec=dec
        )

        for det in self._gbm_detectors:
            if det[0] == "b":

                logger.debug(f"creating BGO reponse for {det} via grb {name}")

                rsp = BGOResponse(det, ra, dec, T0, save=True, name=name)

            else:

                logger.debug(f"creating NAI reponse for {det} via GRB {name}")

                rsp = NaIResponse(det, ra, dec, T0, save=True, name=name)

            bkg = GBMBackground(
                self._background_start,
                self._background_stop,
                average_rate=500,
                detector=det,
            )

            # cpl_source = ConstantCPL(
            #     peak_flux=peak_flux,
            #     trise=trise,
            #     tdecay=duration - trise,
            #     ep_tau=tau,
            #     alpha=alpha,
            #     ep_start=ep,
            #     response=rsp,
            # )

            cpl_source = CPLSourceFunction(
                peak_flux=peak_flux,
                trise=trise,
                tdecay=duration - trise,
                ep_tau=tau,
                alpha=alpha,
                ep_start=ep,
                response=rsp,
            )

            source = Source(0.0, duration, cpl_source, use_plaw_sample=True)

            self._add_lightcurve(
                GBMLightCurve(source, bkg, rsp, name=det, grb_name=self._name)
            )
