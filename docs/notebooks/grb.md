---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import matplotlib.pyplot as plt
import numpy as np
#print(plt.style.available)
import cosmogrb
```

```python
%matplotlib widget
plt.style.use('seaborn-v0_8-pastel') 
```

# GRBs

This section describes how to handle the low level simulation of GRBs. AS the code currently is built for simulating GRBs as observed by Fermi-GBM, we will focus our attention there. As the code expands, I will update the docs. 

![alt text](https://upload.wikimedia.org/wikipedia/commons/1/1f/Fermi_telescope_illustration_01.jpg)



## Instantiate the GRB with its parameters

For this example, we will create a GRB that has its flux coming from a single pulse shape that is described by a cutoff power law evolving in time. 

$$  F_{h\nu}(t)  = K(t) \left(\frac{\nu}{\nu_0(t)} \right)^{-\alpha} \cdot \exp\left(- \frac{\nu}{\nu_0(t)} \right)$$



```python
grb = cosmogrb.gbm.GBMGRB_CPL(
    ra=312.0,
    dec=-62.0,
    z=1.0,
    peak_flux=1e-6,
    alpha=-0.66,
    ep=500.0,
    tau=2.0,
    trise=1.0,
    tdecay=1.0,
    duration=80.0,
    T0=0.1,
)

grb.info()
```

<!-- #region heading_collapsed=true -->
## Examine the latent lightcurve
<!-- #endregion -->

```python hidden=true
time = np.linspace(0, 20, 500)

grb.display_energy_integrated_light_curve(time, color="#A363DE");
```

```python hidden=true
energy = np.logspace(1, 3, 1000)

grb.display_energy_dependent_light_curve(time, energy, cmap='PRGn', lw=.25, alpha=.5)
```

```python
fig,ax = plt.subplots(figsize=(7,5))
time = np.linspace(0, 5, 15)
energy = np.logspace(1, 3, 100)
grb.display_time_dependent_spectrum(time,energy,ax=ax)
ax.set_ylim(1e-3,9e2)
```

## Simulate the GRB 
Now we can create all the light curves from the GRB. Since are not currently running a Dask server, we tell the GRB to process serially, i.e., computing each light curve one at a time.

```python
grb.go(serial=True)
```

## Save the GRB to an HDF5 file

As this is a time-consuming operation, we want to be able to save the GRB to disk. This is done by serializing all the light curves and information about the GRB into an HDF5 file.

```python
grb.save('test_grb.h5')
```

## Reload the GRB

What if want to reload the GRB? We need to create and instance of **GRBSave** from the file we just created. Notice all the information about the GRB is recovered.

```python
grb_reload = cosmogrb.GRBSave.from_file('test_grb.h5')
grb_reload.info()
```

### The GRBSave contents
The stores all the information about the light curves and the instrument responses used to generate the data. Each light curve/ response pair can be accessed as keys of the **GRBSave**. Then one can easily, examine/plot/process the contents of each light curve.


```python
for key in grb_reload.keys():
    
    lightcurve = grb_reload[key]['lightcurve']
    lightcurve.info()
```

For example, let's look at the total, source, and background data light curves generated.

```python tags=["nbsphinx-thumbnail"]
fig, axes = plt.subplots(4,4,sharex=True,sharey=False,figsize=(10,10))
row=0
col = 0
for k,v  in grb_reload.items():
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
plt.tight_layout()
plt.show()
```

And we can look at the generated count spectra/

```python
%matplotlib widget
fig, axes = plt.subplots(4,4,sharex=False,sharey=False,figsize=(10,10))
row=0
col = 0

for k, v in grb_reload.items():
    ax = axes[row][col]
    
    lightcurve = v['lightcurve']
    
    lightcurve.display_count_spectrum(tmin=0, tmax=5,ax=ax,color='#25C68C',label='All')
    lightcurve.display_count_spectrum_source(tmin=0, tmax=5, ax=ax,color="#A363DE",label='Source')
    lightcurve.display_count_spectrum_background(tmin=0, tmax=5, ax=ax, color="#2C342E",label='Bkg')
    ax.set_title(k,size=8)
    
    if col < 3:
        col+=1
    else:
        row+=1
        col=0

axes[0,0].legend()
axes[3,2].set_visible(False)  
axes[3,3].set_visible(False)  
plt.tight_layout()
```

## Convert HDF5 to standard FITS files

In the case of GBM, we can convert the saved HDF5 files into TTE files for analysis in 3ML.

```python
cosmogrb.grbsave_to_gbm_fits("test_grb.h5")
#!ls SynthGRB_*
```

```python

```
