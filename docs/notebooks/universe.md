---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.8.0
  kernelspec:
    display_name: cosmogrb
    language: python
    name: cosmogrb
---

# Simulating a Universe of GRBs
Now we move to the main purpose of the code which is simulating many GRBs from distribution. We will set up a toy model for demonstration. The first thing we need to do is create our population with [popsynth](https://popsynth.readthedocs.io/en/latest/index.html).

```python
# Scientific libraries

import numpy as np

import matplotlib.pyplot as plt
%matplotlib notebook
from jupyterthemes import jtplot

jtplot.style(context='notebook', fscale=1, grid=False)
plt.style.use('mike') 
```

## Create a population of GRBs

Using popsynth, we construct a population. The source parameters to be simulated need to be generated in the population. 


<!-- #raw -->
.. note::
   In the future, a specific format for populations will be defined. This will create a much more user-friendly interface    for creating populations.
<!-- #endraw -->

```python
import popsynth
from popsynth.aux_samplers.normal_aux_sampler import NormalAuxSampler
from popsynth.aux_samplers.trunc_normal_aux_sampler import TruncatedNormalAuxSampler
from popsynth.aux_samplers.lognormal_aux_sampler import LogNormalAuxSampler
```

**cosmogrb** requires certain parameters to be simulated in a population. We will create the auxiliary samplers to do this.


```python
class TDecaySampler(popsynth.AuxiliarySampler):
    def __init__(self):
        """
        samples the decay of the of the pulse 
        """

        super(TDecaySampler, self).__init__(name="tdecay", sigma=None, observed=False)

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values
        trise = self._secondary_samplers["trise"].true_values

        self._true_values = (
            1.0 / 50.0 * (10 * t90 + trise + np.sqrt(trise) * np.sqrt(20 * t90 + trise))
        )


class DurationSampler(popsynth.AuxiliarySampler):
    def __init__(self):
        "samples how long the pulse last"

        super(DurationSampler, self).__init__(
            name="duration", sigma=None, observed=False
        )

    def true_sampler(self, size):

        t90 = 10 ** self._secondary_samplers["log_t90"].true_values

        self._true_values = 1.5 * t90
```

Now that we have creates our extra distribution samplers, we can go ahead and create the population sampler. We will use a simple SFR like redshift distribution and a Pareto (power law) luminosity function

```python
# redshift distribution 
r0_true = 3
rise_true = 1.
decay_true = 4.0
peak_true = 1.5

# the luminosity
Lmin_true = 1e51
alpha_true = 1.5
r_max = 7.0


pop_gen = popsynth.populations.ParetoSFRPopulation(
    r0=r0_true,
    rise=rise_true,
    decay=decay_true,
    peak=peak_true,
    Lmin=Lmin_true,
    alpha=alpha_true,
    r_max=r_max,
)
```

Now set up and add all the auxiliary samplers

```python
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
```

We sample the population. It is important to specify that there is no selection as we will implement the full trigger later.

```python
pop = pop_gen.draw_survey(no_selection=True, boundary=1e-2)
```

```python
pop.display_obs_fluxes_sphere(size=1., cmap='cividis', background_color='black')
```

We save the population to a file for reloading later

```python
pop.writeto("population.h5")
```

## Simulation the population with cosmogrb

We will use dask to handle the parallel generation of all the GRBs in the universe. The code can be run serially as well, but it is possible that the time will be equaivalent to the actual age of the Universe. 


```python
from dask.distributed import LocalCluster, Client
from cosmogrb.instruments.gbm import GBM_CPL_Universe
```

```python
cluster = LocalCluster(n_workers=24)
client = Client(cluster)
client
```

Now we pass the population file to a specialized GBM observed universe. Here GRBs have simple FRED-like pulses and evolving peak $\nu F_{\nu}$ energies. We need to specify as path to save all the generated files. 

```python
universe = GBM_CPL_Universe('population.h5', save_path="/data/jburgess/cosmogrb/")
```

Pass the client to the **go** function and wait while your GRBs go off and have their data recorded by GBM... or whatever instrument is included in the package next.

```python
universe.go(client)
```

When we are done, we will want to save the meta information (file locations, etc) to a file to recover later. We call this object a **Survey**.

```python
.. note::
   In the future, there will be the option to place the entire simulation in one large file to avoid having to keep track of file locations. For now, if once changes the location of the files, further processing of the survey will not be possible
```

```python
universe.save('survey.h5')
```

```python
client.close()
cluster.close()
```

We can now shut off our cluster.


## Processing a Survey
Creating GRBs does not automatically run an instrument's detection algorithm on them as we want to store the raw data and possibly analyze *why* a GRB was not detected as a function of its latent parameters. This is typically an expensive process, so we will again use dask to farm out jobs. 


```python
cluster = LocalCluster(n_workers=24)
client = Client(cluster)
client
```

We must import the trigger analysis class specific to GBM for the survey.  An error will occur if we use the wring class.

```python
from glob import glob
from cosmogrb.universe.survey import Survey
from cosmogrb.instruments.gbm.gbm_trigger import GBMTrigger
```

The survey can be reloaded from the file we saved. All the information about the GRBs which were simulated is contained in the file. We then process the triggers. We selected a trigger threshold of 4.5 $\sigma$ to mimic the true GBM trigger. Afterwards, we will save the survey back to a file, this time with the processed trigger information.

```python
survey = Survey.from_file('survey.h5')
survey.process(GBMTrigger, client=client, threshold=4.5)
survey.write('survey.h5')
```

Upon reloading the survey, we can verify that, indeed, GBM triggered on some of the event!

```python
survey = Survey.from_file('survey.h5')
survey.info()
```




We can can examine one of the detected GRBs

```python
survey['SynthGRB_1'].detector_info.info()
```

```python
fig, axes = plt.subplots(4,4,sharex=True,sharey=False,figsize=(10,10))
row=0
col = 0
for k,v  in survey['SynthGRB_1'].grb.items():
    ax = axes[row][col]
    
    lightcurve =v['lightcurve']
    
    lightcurve.display_lightcurve(dt=.5, ax=ax,lw=1,color='#25C68C')
    lightcurve.display_source(dt=.5,ax=ax,lw=1,color="#A363DE")
    lightcurve.display_background(dt=.5,ax=ax,lw=1, color="#2C342E")
    ax.set_xlim(-10, 30)
    ax.set_title(k,size=8)
    
    
    
    if col < 3:
        col+=1
    else:
        row+=1
        col=0

axes[3,2].set_visible(False)  
axes[3,3].set_visible(False)      
```

as well as examining one that was not detected:

```python
survey['SynthGRB_0'].detector_info.info()
```

```python
fig, axes = plt.subplots(4,4,sharex=True,sharey=False,figsize=(10,10))
row=0
col = 0
for k,v  in survey['SynthGRB_0'].grb.items():
    ax = axes[row][col]
    
    lightcurve =v['lightcurve']
    
    lightcurve.display_lightcurve(dt=.5, ax=ax,lw=1,color='#25C68C')
    lightcurve.display_source(dt=.5,ax=ax,lw=1,color="#A363DE")
    lightcurve.display_background(dt=.5,ax=ax,lw=1, color="#2C342E")
    ax.set_xlim(-10, 30)
    ax.set_title(k,size=8)
    
    
    
    if col < 3:
        col+=1
    else:
        row+=1
        col=0

axes[3,2].set_visible(False)  
axes[3,3].set_visible(False)      
```

```python

```
