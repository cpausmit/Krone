#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Modeling of an outbreak.
#
# SIR implementation readup at:
#    https://towardsdatascience.com/infection-modeling-part-1-87e74645568a
#
# The detailed model I am just making it up on the way.
#
#---------------------------------------------------------------------------------------------------
import sys,os,getopt
import datetime
import numpy
# Our stuff
import history
import rgvd
import pathogen
import population

#===================================================================================================
# MAIN
#===================================================================================================
# Define string to explain usage of the script
usage  = "\nUsage: outbreak.py [ --n_popul=<int> --i_initial=<int> --n_day_max=<int> \
                                 --reco_mean=<float> --reco_std=<float> --pi_inital=<float>\
                                 --pi_decay=<float> --death_rate=<float> --exposure_avg=<float>\
                                 --exposure_std=<float> --seed=<int> --record=<string>\
                                 --date=<string>]\n"

valid = ['n_popul=','i_initial=','n_day_max=','reco_mean=','reco_std=','pi_initial=','pi_decay=',
         'death_rate=','exposure_avg=','exposure_std=','seed=','record=','date=',
         'help']
try:
    opts, args = getopt.getopt(sys.argv[1:], "", valid)
except getopt.GetoptError, ex:
    print usage
    print str(ex)
    sys.exit(1)

# As an example of this, we will use a 62 node social network constructed from interactions within a
# pod of dolphins. Let's take the example of an infection that has an average recovery time r of 30
# days (standard deviation of 8 days), and an average transmission probability p of 6% (standard
# deviation of 1%) that decays by 10% each day of a node's infection. Let's further take the
# scenario that two nodes (n=2), chosen randomly, are the source of the infection in the network.

# As an example of this, we will use a Massachusetts with 6.883M inhabitants.  The corona virus has
# an average recovery time r of 14 days (standard deviation of 5 days), and an average transmission
# probability p of 2.92% that decays by 10% each day of a node's infection. The infection is
# initiated at a given day, 2020-03-31, with 6620 people, chosen randomly, as the source of the
# infection in the network. The Network implementation is a little more complicated but is specified
# in the code. The death rate is taken to be 4% according to information from various sources that
# seem to be reasonably solid.

# input parameters for the SIR modelling
N_POPULATION = 6883000
N_DAYS = 20
I_INITIAL = 6620
RECO_MEAN = 12.8
RECO_STD = 4.5
PI_INITIAL = 0.0305
PI_DECAY = 0.10
DEATH_RATE = 0.0273
EXPOSURE_AVG = 5
EXPOSURE_STD = 2
SEED = 1000
RECORD = "data/time_series_covid19"
DATE = "2020-03-31"

R_UNKNOWN = 4

date_s = datetime.datetime.strptime(DATE, "%Y-%m-%d")

# read all command line options
for opt, arg in opts:
    if opt == "--help":
        print usage
        sys.exit(0)
    if opt == "--debug":
        debug = True
    if opt == "--n_popul":
        N_POPULATION = int(arg)
    if opt == "--i_initial":
        I_INITIAL = int(arg)
    if opt == "--n_day_max":
        N_DAYS = int(arg)
    if opt == "--reco_mean":
        RECO_MEAN = float(arg)
    if opt == "--pi_initial":
        PI_INITIAL = float(arg)
    if opt == "--pi_decay":
        PI_DECAY = float(arg)
    if opt == "--exposure_mean":
        EXPOSURE_AVG = int(arg)
    if opt == "--exposure_std":
        EXPOSURE_STD = int(arg)
    if opt == "--seed":
        SEED = int(arg)
    if opt == "--date":
        DATE = arg
    if opt == "--record":
        RECORD = arg

# Propagate input

corona = pathogen.Pathogen(rgvd.Rgvd(RECO_MEAN,RECO_STD,1),PI_INITIAL,PI_DECAY,DEATH_RATE)
social_type = population.Social_type(rgvd.Rgvd(EXPOSURE_AVG,EXPOSURE_STD,1),4,200,0.1)
numpy.random.seed(seed=int(SEED))

# Generate the population

id = 0
popul = population.Population()

while (popul.n()<N_POPULATION):
    p = population.Person(id,social_type)
    popul.add_person(p)

    id += 1 # increase index for the next person
print "Day: %d  == %s"%(-1, popul.summary())

# Generate an infection in the healthy population
n = popul.n()
while (popul.i() < I_INITIAL * 4):
    id = numpy.random.randint(0,n)
    popul.infect(id,corona)
print "Day: %d == %s"%(0, popul.summary())

# Propagate our spreading model
i_days = 0
history = history.History(RECORD)
today = date_s

print " Corona virus: %s"%(corona.summary())
while (i_days<N_DAYS):

    # record history
    history.add_day(today,len(popul.infected),len(popul.recovered),len(popul.deceased))
    print "Day: %d (%s) == %s"%(i_days, today, popul.summary())
    
    # spread and check whether it is still active
    popul.spread(corona)

    # increase the day
    i_days += 1
    today = today + datetime.timedelta(days=1)
    if not popul.is_active(today,i_days):
        history.add_day(today,len(popul.infected),len(popul.recovered),len(popul.deceased))
        history.write()
        sys.exit(0)


# completed all steps of the simulation but pathogen is still active
print "Day: %d (%s) == %s"%(i_days, today, popul.summary())
history.write()
