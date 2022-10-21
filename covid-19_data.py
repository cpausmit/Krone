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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import sys,os,getopt
import datetime

#===================================================================================================
# HELPERS
#===================================================================================================
def chi2(imin,imax,values,values_mc):
    chi2 = 0
    for i in range(imin,imax+1):
        delta = values[i]-values_mc[i-imin]
        chi2 += delta*delta/values[i]
    return chi2

def find_xoverlap(times,times_mc):

    imin_data = 0
    if times_mc[0]>times[0]:
        for time in times:
            if time<times_mc[0]:
                imin_data += 1


    imax_data = len(times)-1

    return imin_data,imax_data

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
            imax = i
        if t>time_max:
            break
        i += 1

    # return the indices
    return imin,imax

def update_file(get_cmd,data_url,data_file):
    print " Update the data file: %s"%data_file
    cmd = "%s %s -O data/%s >& /dev/null"%(get_cmd,data_url,data_file)
    os.system(cmd)
    return

def read_data(data_file,delta,us,scale=1.0):
    print " Reading the data from: %s"%data_file
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
    if delta:
        ax.set_ylabel('Number of New %s / day'%value_name)
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
usage  = "\nUsage: covid-19_data.py --tags=tag1,tag43,tag300 [ --tmin=<first-day> --tmax=<last-day> --vmax=<nmax> --deaths --delta --logy --logx --us --mc --mc_file=<file> --quiet ]\n"
valid = ['tags=','tmin=','tmax=','vmax=','debug','update','death','delta','logy','logx','us','sim','mc','mc_file=','quiet','help']
try:
    opts, args = getopt.getopt(sys.argv[1:], "", valid)
except getopt.GetoptError, ex:
    print usage
    print str(ex)
    sys.exit(1)

# read all command line options
tags = [ 'Germany' ]
tmin = 0
tmax = 0
vmax = 0
update = False
death = False
delta = False
logx = False
logy = False
us = False
sim = False
mc = False
mc_file = ""
quiet = False
for opt, arg in opts:
    if opt == "--help":
        print usage
        sys.exit(0)
    if opt == "--debug":
        debug = True
    if opt == "--tags":
        tags = arg.split(",")
    if opt == "--tmin":
        tmin = arg
    if opt == "--tmax":
        tmax = arg
    if opt == "--vmax":
        vmax = int(arg)
    if opt == "--death":
        death = True
    if opt == "--update":
        update = True
    if opt == "--delta":
        delta = True
    if opt == "--logx":
        logx = True
    if opt == "--logy":
        logy = True
    if opt == "--us":
        us = True
    if opt == "--sim":
        sim = True
    if opt == "--mc":
        mc = True
    if opt == "--mc_file":
        mc_file = arg
    if opt == "--quiet":
        quiet = True

# determine which input
value_name = 'Infected'
if death:
    value_name = 'Deaths'

if us:
    web_file = web_file_confirmed_us
    if death:
        web_file = web_file_deaths_us
elif sim:
    web_file = web_file_confirmed_simus
    if death:
        web_file = web_file_deaths_simus
else:
    web_file = web_file_confirmed
    if death:
        web_file = web_file_deaths

web_file_mc = web_file_confirmed_simus
if death:
    web_file_mc = web_file_deaths_simus

if mc_file != "":
    web_file_mc = mc_file

data_url = "%s/%s/%s"%(web_site,web_dir,web_file)
get_cmd = "wget"

# deal with the input data
if update:
    update_file(get_cmd,data_url,web_file)
(times,values) = read_data(web_file,delta,us)
# just in case you want MC
if mc:
    (times_mc,values_mc) = read_data(web_file_mc,delta,us,0.25)

### # NEW - ALTERNATIVE
### # deal with the input data
### data = data_ts.Data_ts()
### if update:
###     data.update_files()
### data.load_data()
### times = data.times
### if death:
###     values = data.deceased
### else:
###     values = data.infected

# create the data frames and select the data from our container
times = pd.DatetimeIndex(times)
# cut out relevant sub arrays
xmin,xmax = find_xlimits(times,tmin,tmax)
imin,imax = trim_times_series_ids(xmin,xmax,times)
times = times[imin:imax]
for tag in tags:
    values[tag] = values[tag][imin:imax]

if mc:
    times_mc = pd.DatetimeIndex(times_mc)
    # cut out relevant sub arrays
    imin_mc,imax_mc = trim_times_series_ids(tmin,tmax,times_mc)
    times_mc = times_mc[imin_mc:imax_mc]
    for tag in tags:
        values_mc[tag] = values_mc[tag][imin_mc:imax_mc]

    # calculate the chi2
    imin,imax = find_xoverlap(times,times_mc)
    for tag in tags:
        chi2 = chi2(imin,imax,values[tag],values_mc[tag])
        print " Chi2: %f"%chi2

# prepare the plot
set_plot_style(logx,logy,delta,value_name)

# plot
for tag in tags:
    plt.errorbar(times, values[tag], yerr=np.sqrt(values[tag]), marker='o', label=tag)
    if mc:
        plt.errorbar(times_mc, values_mc[tag], yerr=0, label='MC')


if vmax != 0:
    ymax = vmax
    plt.ylim(0,ymax)

plt.xlim(xmin,xmax)
plt.legend(frameon=False)
if not quiet:
    plt.show()

sys.exit(0)
