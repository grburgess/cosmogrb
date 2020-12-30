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
    display_name: Python3
    language: python
    name: Python3
---

# Introduction


**cosmogrb** is a package built upon [popsynth](https://popsynth.readthedocs.io/en/latest/) to simulate GRBs from luminosity functions and various other distributions. Each GRB can be passed through an instrument's response resulting in data when can be later analyzed (preferably with [3ML](https://threeml.readthedocs.io/en/latest/)). Thus, one can generate catalogs of data from theoretical assumptions an test what these assumptions lead to in terms of observation. 

The code is currently in *alpha* so do not expect too much use out of it. 

![alt text](https://raw.githubusercontent.com/grburgess/cosmogrb/master/logo.png)
