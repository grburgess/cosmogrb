import numpy as np

from cosmogrb.instruments.gbm.gbm_grb import GBMGRB_CPL, GBMGRB_CPL_Constant, GBMGRB_SUBPHOTO
from cosmogrb.universe.universe import GRBWrapper, ParameterServer, Universe


class GBM_CPL_Universe(Universe):
    """Documentation for GBM_CPL_Universe

    """

    def __init__(self, population, save_path="."):

        super(GBM_CPL_Universe, self).__init__(population, save_path=save_path)

    def _grb_wrapper(self, parameter_server: ParameterServer, serial: bool=False):
        return GBM_CPL_Wrapper(parameter_server, serial=serial)

    def _process_populations(self):

        # get the Ra and Dec
        super(GBM_CPL_Universe, self)._process_populations()

        self._local_parameters["ep_start"] = self._population.ep
        self._local_parameters["alpha"] = self._population.alpha
        self._local_parameters["peak_flux"] = self._population.fluxes_latent
        self._local_parameters["trise"] = self._population.trise
        self._local_parameters["tdecay"] = self._population.tdecay
        self._local_parameters["ep_tau"] = self._population.tau

    def _parameter_server_type(self, **kwargs):

        return GBM_CPL_ParameterServer(**kwargs)


class GBM_CPL_Wrapper(GRBWrapper):
    """Documentation for GBM_CPL_Wrapper

    """

    def __init__(self, parameter_server, serial=False):
        super(GBM_CPL_Wrapper, self).__init__(
            parameter_server=parameter_server, serial=serial
        )

    def _grb_type(self, **kwargs):
        return GBMGRB_CPL(**kwargs)


class GBM_CPL_ParameterServer(ParameterServer):
    """Documentation for GBM_CPL_ParameterServer

    """

    def __init__(
        self,
        name,
        ra,
        dec,
        z,
        duration,
        T0,
        peak_flux,
        alpha,
        ep_start,
        ep_tau,
        trise,
        tdecay,
    ):
        """FIXME! briefly describe function

        :param name: 
        :param ra: 
        :param dec: 
        :param z: 
        :param duration: 
        :param T0: 
        :param peak_flux: 
        :param alpha: 
        :param ep: 
        :param tau: 
        :param trise: 
        :param tdecay: 
        :returns: 
        :rtype: 

        """

        super(GBM_CPL_ParameterServer, self).__init__(
            name=name,
            ra=ra,
            dec=dec,
            z=z,
            duration=duration,
            T0=T0,
            peak_flux=peak_flux,
            alpha=alpha,
            ep_start=ep_start,
            ep_tau=ep_tau,
            trise=trise,
            tdecay=tdecay,
        )


#
#
#
#


        
class GBM_CPL_Constant_Universe(Universe):
    """Documentation for GBM_CPL_Constant_Universe

    """

    def __init__(self, population, save_path="."):

        super(GBM_CPL_Constant_Universe, self).__init__(
            population, save_path=save_path)

    def _grb_wrapper(self, parameter_server, serial=False):
        return GBM_CPL_Constant_Wrapper(parameter_server, serial=serial)

    def _process_populations(self):

        # get the Ra and Dec
        super(GBM_CPL_Constant_Universe, self)._process_populations()

        self._local_parameters["ep"] = self._population.ep
        self._local_parameters["alpha"] = self._population.alpha
        self._local_parameters["peak_flux"] = self._population.fluxes_latent

    def _parameter_server_type(self, **kwargs):

        return GBM_CPL_Constant_ParameterServer(**kwargs)


class GBM_CPL_Constant_Wrapper(GRBWrapper):
    """Documentation for GBM_CPL_Constant_Wrapper

    """

    def __init__(self, parameter_server, serial=False):
        super(GBM_CPL_Constant_Wrapper, self).__init__(
            parameter_server=parameter_server, serial=serial
        )

    def _grb_type(self, **kwargs):
        return GBMGRB_CPL_Constant(**kwargs)


class GBM_CPL_Constant_ParameterServer(ParameterServer):
    """Documentation for GBM_CPL_Constant_ParameterServer

    """

    def __init__(
        self,
        name,
        ra,
        dec,
        z,
        duration,
        T0,
        peak_flux,
        alpha,
        ep

    ):
        """FIXME! briefly describe function

        :param name: 
        :param ra: 
        :param dec: 
        :param z: 
        :param duration: 
        :param T0: 
        :param peak_flux: 
        :param alpha: 
        :param ep: 
        :returns: 
        :rtype: 

        """

        super(GBM_CPL_Constant_ParameterServer, self).__init__(
            name=name,
            ra=ra,
            dec=dec,
            z=z,
            duration=duration,
            T0=T0,
            peak_flux=peak_flux,
            alpha=alpha,
            ep=ep,

        )

class GBM_SUBPHOTO_Universe(Universe):
    """Documentation for GBM_CPL_Constant_Universe

    """

    def __init__(self, population, save_path="."):

        super(GBM_SUBPHOTO_Universe, self).__init__(
            population, save_path=save_path)

    def _grb_wrapper(self, parameter_server, serial=False):
        return GBM_SUBPHOTO_Wrapper(parameter_server, serial=serial)

    def _process_populations(self):

        # get the Ra and Dec
        super(GBM_SUBPHOTO_Universe, self)._process_populations()

        self._local_parameters["K"] = self._population.K
        self._local_parameters["xi_b"] = self._population.xi_b
        self._local_parameters["r_0"] = self._population.r_0
        self._local_parameters["r_i"] = self._population.r_i
        self._local_parameters["gamma"] = self._population.gamma
        self._local_parameters["l_grb"] = self._population.luminosities_latent
        
    def _parameter_server_type(self, **kwargs):

        return GBM_SUBPHOTO_ParameterServer(**kwargs)


class GBM_SUBPHOTO_Wrapper(GRBWrapper):
    """Documentation for GBM_CPL_Constant_Wrapper

    """

    def __init__(self, parameter_server, serial=False):
        super(GBM_SUBPHOTO_Wrapper, self).__init__(
            parameter_server=parameter_server, serial=serial
        )

    def _grb_type(self, **kwargs):
        return GBMGRB_SUBPHOTO(**kwargs)


class GBM_SUBPHOTO_ParameterServer(ParameterServer):
    """Documentation for GBM_CPL_Constant_ParameterServer

    """

    def __init__(
        self,
        name,
        ra,
        dec,
        z,
        duration,
        T0,
        K,
        xi_b,
        r_i,
        r_0,
        gamma,
        l_grb
    ):
        """FIXME! briefly describe function

        :param name: 
        :param ra: 
        :param dec: 
        :param z: 
        :param duration: 
        :param T0: 
        :param peak_flux: 
        :param alpha: 
        :param ep: 
        :returns: 
        :rtype: 

        """

        super(GBM_SUBPHOTO_ParameterServer, self).__init__(
            name=name,
            ra=ra,
            dec=dec,
            z=z,
            duration=duration,
            T0=T0,
            K=K,
            xi_b=xi_b,
            r_i=r_i,
            r_0=r_0,
            gamma=gamma,
            l_grb=l_grb)
