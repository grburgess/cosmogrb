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


class TDecaySampler(popsynth.AuxiliarySampler):
    def __init__(self):

        super(TDecaySampler, self).__init__(name="tdecay", observed=False)

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values
        trise = self._secondary_samplers["trise"].true_values

        self._true_values = (
            1.0 / 50.0 * (10 * t90 + trise + np.sqrt(trise) * np.sqrt(20 * t90 + trise))
        )


class DurationSampler(popsynth.AuxiliarySampler):
    def __init__(self):

        super(DurationSampler, self).__init__(
            name="duration", observed=False
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


ep = LogNormalAuxSampler(name="log_ep", observed=False)
ep.mu = 500
ep.tau = 0.5

alpha = TruncatedNormalAuxSampler(name="alpha", observed=False)

alpha.lower = -1.5
alpha.upper = 0.0
alpha.mu = -1.0
alpha.tau = 0.25


tau = TruncatedNormalAuxSampler(name="tau", observed=False)

tau.lower = 1.5
tau.upper = 2.5
tau.mu = 2.0
tau.tau = 0.25


trise = TruncatedNormalAuxSampler(name="trise", observed=False)

trise.lower = 0.01
trise.upper = 5.0
trise.mu = 1.0
trise.tau = 1.0


t90 = LogNormalAuxSampler(name="log_t90", observed=False)

t90.mu = 10
t90.tau = 0.25


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
