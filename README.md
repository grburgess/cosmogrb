[![Travis CI w/ Logo](https://img.shields.io/travis/grburgess/cosmogrb/master.svg?logo=travis)](https://travis-ci.org/grburgess/cosmogrb)
[![codecov](https://codecov.io/gh/grburgess/cosmogrb/branch/master/graph/badge.svg)](https://codecov.io/gh/grburgess/cosmogrb)

# cosmogrb

## Idea
This simulates a cosmological population of **GRBs** in the Universe from a given space and luminosity distribution.

### Light curves / lightcurves

After simulation, a realistic background and temporally evolving spectrum are created. These are then sampled at the single photon level, pushed through the detector responses, simulated with real dead time, and pushed into FITS Event files. 

Cool?
