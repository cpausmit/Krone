#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Simple data analysis tool to plot the time series for COVID-19 developments.
#
# This tool is python based and uses the following packages:
#
#    sudo dnf install python-numpy python-matplotlib python-pandas
#
#---------------------------------------------------------------------------------------------------
import data_ts

import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import sys,os,getopt
import datetime
# initial settings
mlp.rcParams['axes.linewidth'] = 2

#===================================================================================================
# HELPERS
#===================================================================================================
def find_xlimits(times,tmin,tmax):
    xmin = times[0]
    xmax = times[-1]

    if tmin != 0:
        xmin = tmin
    if tmax != 0:
        xmax = tmax

    return xmin,xmax

def trim_times_series_ids(tmin,tmax,times):

    # convert date limits into times

    try:
        tmin = str(tmin.date())
    except:
        pass

    try:
        tmax = str(tmax.date())
    except:
        pass

    time_min = datetime.datetime.strptime(tmin,"%Y-%m-%d")
    time_max = datetime.datetime.strptime(tmax,"%Y-%m-%d")

    # find indices looking into times array
    imin = -1
    imax = -1
    i = 0
    for time in times:
        t = datetime.datetime.strptime(str(time)[0:10],"%Y-%m-%d")
        if imin == -1 and t>=time_min:
            imin = i
        if t<=time_max:
            imax = i+1
        if t>time_max:
            imax = i+1
            break
        i += 1

    # return the indices
    return imin,imax

def update_file(get_cmd,data_url,data_file):
    if not quiet:
        print(" Update the data file: %s"%data_file)
    cmd = "%s %s -O data/%s >& /dev/null"%(get_cmd,data_url,data_file)
    os.system(cmd)
    return

def read_data(data_file,delta,us,scale=1.0):
    if not quiet:
        print(" Reading the data from: %s"%data_file)
    # set the offset
    n_offset = 4
    n_tag = 1
    if us:
        n_offset = 11
        n_tag = 6

    # loop the file
    with open("data/%s"%data_file,'r') as csvfile:
        ts_file = csv.reader(csvfile, delimiter=',')
        times = []
        values = {}
        for row in ts_file:
            if len(times) == 0:
                times = row[n_offset:]
                continue

            # read this line as the next timeseries values, might have to be added to existing
            tag = row[n_tag]

            # find existing series or create empty one
            if tag in values.keys():
                series = values[tag]
            else:
                series = [ 0 ] * len(times)

            # loop through the values and convert to integer
            tmp_values = []
            for value in row[n_offset:]:
                tmp_values.append(int(value))

            series = [x+y for x,y in zip(series,tmp_values)]

            values[tag] = series

    # loop through all series and calculate delta N (assume day before first day == first day)
    if delta:
        for tag in values.keys():
            vs = values[tag]
            res = [vs[i+1] - vs[i] for i in range(len(vs)-1)] # successive difference list
            res.insert(0,0)
            values[tag] = res
    if scale != 1:
        for tag in values.keys():
            values[tag] = [x * scale for x in values[tag]]

    return (times, values)

def set_plot_style(logx,logy,delta,value_name):
    SMALL_SIZE = 22
    MEDIUM_SIZE = 30
    BIGGER_SIZE = 32

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    figure = plt.figure(figsize=(12,11))

    figure.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.05)
    if logy:
        figure.subplots_adjust(left=0.11)

    ax = figure.add_subplot(111)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of %s'%value_name)
    if relative:
        ax.set_ylabel('Pop. percentage of %s [%%]'%(value_name))
    if delta:
        ax.set_ylabel('Number of new %s / day'%(value_name))
        if combine > 1:
            ax.set_ylabel('Number of new %s / %d days'%(value_name,combine))
        if relative:
            ax.set_ylabel('Pop. percentage of new %s / day [%%]'%(value_name))
            if combine > 1:
                ax.set_ylabel('Pop. percentage of new %s / %d days [%%]'%(value_name,combine))
    figure.autofmt_xdate()
    figure.subplots_adjust(bottom=0.17)
    if logx:
        plt.xscale("log")
    if logy:
        plt.yscale("log")

    return

# also interesting:
## https://www.worldometers.info/coronavirus/?fbclid=IwAR0mcv7OMDgSGj5CoQ0I0v49EVYCFGbqk1G7FefuzjjPpsG_6rfSw8IOL4k

web_site = "https://raw.githubusercontent.com"
web_dir = "CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"
web_file_confirmed = "time_series_covid19_confirmed_global.csv"
web_file_deaths = "time_series_covid19_deaths_global.csv"
web_file_confirmed_us = "time_series_covid19_confirmed_US.csv"
web_file_deaths_us = "time_series_covid19_deaths_US.csv"
web_file_confirmed_simus = "time_series_covid19_confirmed_SIMUS.csv"
web_file_deaths_simus = "time_series_covid19_deaths_SIMUS.csv"

#===================================================================================================
# MAIN
#===================================================================================================
# Define string to explain usage of the script
usage  = "\nUsage: covid-19_data.py --tags=tag1,tag43,tag300 [ --tmin=<first-day:%Y-%m-%d> --tmax=<last-day:%Y-%m-%d> --vmax=<nmax> --deaths --delta --relative --logy --logx --nopng --noplot --quiet ]\n"
valid = ['tags=','tmin=','tmax=','vmax=','combine=','debug','update','death','delta','relative','logy','logx','us','sim','mc','mc_file=','nopng','quiet','help']

#except ex as getopt.GetoptError:
#    try:
#        opts, args = getopt.getopt(sys.argv[1:], "", valid)
#    finally:
#        print(usage)
#        print(str(ex))
#        sys.exit(1)
opts, args = getopt.getopt(sys.argv[1:], "", valid)
        
# read all command line options
tags = [ 'US','Massachusetts','Switzerland','France']
tmin = 0
tmax = 0
vmax = 0
combine = 1
update = False
death = False
delta = False
relative = False
logx = False
logy = False
us = False
sim = False
mc = False
mc_file = ""
quiet = False
nopng = False
noplot = False

for opt, arg in opts:
    if opt == "--help":
        print(usage)
        sys.exit(0)
    if opt == "--debug":
        debug = True
    if opt == "--tags":
        tags = arg.split(",")
    if opt == "--tmin":
        tmin = pd.DatetimeIndex([arg])[0]
        tmin = datetime.datetime.strptime(arg,'%Y-%m-%d')
    if opt == "--tmax":
        tmax = datetime.datetime.strptime(arg,'%Y-%m-%d')
    if opt == "--vmax":
        vmax = int(arg)
    if opt == "--combine":
        combine = max(1,int(arg))
    if opt == "--death":
        death = True
    if opt == "--update":
        update = True
    if opt == "--delta":
        delta = True
    if opt == "--relative":
        relative = True
    if opt == "--logx":
        logx = True
    if opt == "--logy":
        logy = True
    if opt == "--quiet":
        quiet = True
    if opt == "--nopng":
        nopng = True
    if opt == "--noplot":
        noplot = True

# determine which input
value_name = 'Infected'
if death:
    value_name = 'Deaths'

# deal with the input data
data = data_ts.Data_ts("%s/data"%(os.environ.get('KRONE_BASE')))
if update:
    data.update_files(quiet)
data.load_data(quiet)
data.combine_values(combine)
# not working ?! # data.rolling_values(combine)
data.summary()

# create the data axis points
times = pd.DatetimeIndex(data.times)

# want to look at deaths or infections
if death:
    values = data.deceased
else:
    values = data.infected

# want to look at cummulative or deltas
if delta:
    for tag in tags:
        values[tag][1:] = np.diff(values[tag])
        values[tag][0] = 0

# relative to total population in percent
if relative:
    for tag in tags:
        if not quiet:
            print(" Area(%s), Population: %d"%(tag,data.population[tag]))
        values[tag] = np.array(values[tag]) * (100./float(data.population[tag]))
       
# cut out relevant sub arrays
xmin,xmax = find_xlimits(times,tmin,tmax)
if not quiet:
    print(" %s - %s "%(xmin,xmax))
imin,imax = trim_times_series_ids(xmin,xmax,times)
times = pd.DatetimeIndex(times[imin:imax])
for tag in tags:
    values[tag] = values[tag][imin:imax]
    
# prepare the plot
set_plot_style(logx,logy,delta,value_name)

# plot
for tag in tags:
    #plt.errorbar(times, values[tag], yerr=np.sqrt(values[tag]), marker='o', label=tag)
    plt.plot(times, values[tag], marker='o', label=tag)

if vmax != 0:
    ymax = vmax
    plt.ylim(0,ymax)

delta = 0.02*(xmax-xmin)
plt.xlim(xmin-delta,xmax+delta)
plt.legend(frameon=False)

if not nopng:
    plt.savefig('./c19.png')
if not noplot:
    plt.show()

sys.exit(0)
