#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Simple data analysis tool to plot the time series for COVID-19 developments.
#
# This tool is python based and uses the following packages:
#
#    sudo dnf install python-numpy python-matplotlib python-pandas
#
#---------------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import sys,os,getopt

def exp(t):
    delta = -0.1
    a = 1
    b = 0
    return a*np.exp(t*delta)+b

t = np.arange(0.0, 5.0, 0.1)

for tmp in t:
    print " f(%f) = %f"%(tmp,exp(tmp))

plt.plot(t,exp(t))
plt.ylim(0,1.1)
plt.show()
