from cosmogrb.instruments.gbm import GBMGRB_CPL
import popsynth
from popsynth.aux_samplers.normal_aux_sampler import NormalAuxSampler
from popsynth.aux_samplers.trunc_normal_aux_sampler import TruncatedNormalAuxSampler
from popsynth.aux_samplers.lognormal_aux_sampler import LogNormalAuxSampler

from cosmogrb.instruments.gbm import GBM_CPL_Universe

from dask.distributed import Client, LocalCluster

import numpy as np


# this is a script that is used to generate the test data for the
# pytest. it is meant to be run from the top of the pacakge


grb = GBMGRB_CPL(
    ra=312.0,
    dec=-62.0,
    z=1.0,
    peak_flux=5e-7,
    alpha=-0.66,
    ep=500.0,
    tau=2.0,
    trise=1.0,
    tdecay=1.0,
    duration=80.0,
    T0=0.1,
)

grb.go(client=None, serial=True)


grb.save("cosmogrb/data/test_grb.h5")


grb = GBMGRB_CPL(
    ra=312.0,
    dec=-62.0,
    z=1.0,
    peak_flux=5e-20,
    alpha=-0.66,
    ep=500.0,
    tau=2.0,
    trise=1.0,
    tdecay=1.0,
    duration=80.0,
    T0=0.1,
)

grb.go(client=None, serial=True)


grb.save("cosmogrb/data/weak_grb.h5")


class TDecaySampler(popsynth.AuxiliarySampler):
    def __init__(self):

        super(TDecaySampler, self).__init__(name="tdecay", sigma=None, observed=False)

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values
        trise = self._secondary_samplers["trise"].true_values

        self._true_values = (
            1.0 / 50.0 * (10 * t90 + trise + np.sqrt(trise) * np.sqrt(20 * t90 + trise))
        )


class DurationSampler(popsynth.AuxiliarySampler):
    def __init__(self):

        super(DurationSampler, self).__init__(
            name="duration", sigma=None, observed=False
        )

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values

        self._true_values = 1.5 * t90


r0_true = 0.13
rise_true = 0.1
decay_true = 4.0
peak_true = 1.5


td_true = 3.0
sigma_true = 1.0

Lmin_true = 1e50
alpha_true = 1.5
r_max = 5.0


pop_gen = popsynth.populations.ParetoSFRPopulation(
    r0=r0_true,
    rise=rise_true,
    decay=decay_true,
    peak=peak_true,
    Lmin=Lmin_true,
    alpha=alpha_true,
    r_max=r_max,
)


ep = LogNormalAuxSampler(mu=300.0, tau=0.5, name="log_ep", observed=False)
alpha = TruncatedNormalAuxSampler(
    lower=-1.5, upper=0.1, mu=-1, tau=0.25, name="alpha", observed=False
)
tau = TruncatedNormalAuxSampler(
    lower=1.5, upper=2.5, mu=2, tau=0.25, name="tau", observed=False
)
trise = TruncatedNormalAuxSampler(
    lower=0.01, upper=5.0, mu=1, tau=1.0, name="trise", observed=False
)
t90 = LogNormalAuxSampler(mu=10, tau=0.25, name="log_t90", observed=False)

tdecay = TDecaySampler()
duration = DurationSampler()
tdecay.set_secondary_sampler(t90)
tdecay.set_secondary_sampler(trise)

duration.set_secondary_sampler(t90)


pop_gen.add_observed_quantity(ep)
pop_gen.add_observed_quantity(tau)
pop_gen.add_observed_quantity(alpha)
pop_gen.add_observed_quantity(tdecay)
pop_gen.add_observed_quantity(duration)

pop = pop_gen.draw_survey(no_selection=True, boundary=1e-2)


pop.writeto("cosmogrb/data/test_grb_pop.h5")
