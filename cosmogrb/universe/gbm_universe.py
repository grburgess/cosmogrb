from cosmogrb.universe.universe import Universe, GRBWrapper, ParameterServer
from cosmogrb.grb import GBMGRB_CPL


class GBM_CPL_Universe(Universe):
    """Documentation for GBM_CPL_Universe

    """

    def __init__(self):

        super(GBM_CPL_Universe, self).__init__()

    def _grb_wrapper(self):
        return GBM_CPL_Wrapper


class GBM_CPL_Wrapper(GRBWrapper):
    """Documentation for GBM_CPL_Wrapper

    """

    def __init__(self, parameter_server):
        super(GBM_CPL_Wrapper, self).__init__()
        self._parameter_server = parameter_server

    def _grb_type(self):
        return GBMGRB_CPL


class GBM_CPL_ParameterServer(ParameterServer):
    """Documentation for GBM_CPL_ParameterServer

    """

    def __init__(
        self, name, ra, dec, z, duration, T0, peak_flux, alpha, ep, tau, trise, tdecay
    ):
        super(GBM_CPL_ParameterServer, self).__init__(
            name=name,
            ra=ra,
            dec=dec,
            z=z,
            duration=duration,
            T0=T0,
            peak_flux=peak_flux,
            alpha=alpha,
            ep=ep,
            tau=tau,
            trise=trise,
            tdecay=tdecay,
        )
