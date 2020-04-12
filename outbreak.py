#!/usr/bin/env python
import sys,os,getopt
import datetime
import numpy
#---------------------------------------------------------------------------------------------------
# Modeling of an outbreak.
#
# SIR implementation readup at:
#    https://towardsdatascience.com/infection-modeling-part-1-87e74645568a
#
#---------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------
"""
Class:  History(record)

     Description of the relevant history of the outbreak of an infectious disease.

       record    - the file where to record (only done at the end, maybe need to change that)

       dates     - times series dates (list)
       infected  - number of infected people per day (list)
       recovered - number of recovered people per day (list)
       deceased  - number of deceased people per day (list)

"""
class History:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,record):
        self.record = record
        self.header_base = \
            "UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,Long_,Combined_Key"
        self.data_base = \
            "84025017,US,USA,840,25017.0,Middlesex,Massachusetts,US,42.48607732,-71.39049229,\"Middlesex, Massachusetts, US\""
        self.dates = []
        self.infected = []
        self.recovered = []
        self.deceased = []
        
    #-----------------------------------------------------------------------------------------------
    # summary as a string
    #-----------------------------------------------------------------------------------------------
    def summary(self):
        range = " History: EMPTY"
        if len(self.dates):
            range = "History: "%(self.dates[0],self.dates[-1])
        return range
         
        
    #-----------------------------------------------------------------------------------------------
    # add another day
    #-----------------------------------------------------------------------------------------------
    def add_day(self,date,n_infected,n_recovered,n_deceased):
        self.dates.append(date)
        self.infected.append(n_infected)
        self.recovered.append(n_recovered)
        self.deceased.append(n_deceased)

    #-----------------------------------------------------------------------------------------------
    # record history to its file
    #-----------------------------------------------------------------------------------------------
    def write(self):
        # two lines per file: header and data
        with open("%s_confirmed_SIMUS.csv"%self.record,'w') as csvfile:
            
            csvfile.write(self.header_base)
            for date in self.dates:
                csvfile.write(",%s"%date)
            csvfile.write("\n")

            csvfile.write(self.data_base)
            for i in self.infected:
                csvfile.write(",%d"%i)
            csvfile.write("\n")
            
        with open("%s_recovered_SIMUS.csv"%self.record,'w') as csvfile:

            csvfile.write(self.header_base)
            for date in self.dates:
                csvfile.write(",%s"%date)
            csvfile.write("\n")

            csvfile.write(self.data_base)
            for r in self.recovered:
                csvfile.write(",%d"%r)
            csvfile.write("\n")

        with open("%s_deaths_SIMUS.csv"%self.record,'w') as csvfile:

            csvfile.write(self.header_base)
            for date in self.dates:
                csvfile.write(",%s"%date)
            csvfile.write("\n")

            csvfile.write(self.data_base)
            for d in self.deceased:
                csvfile.write(",%d"%d)
            csvfile.write("\n")
        
#---------------------------------------------------------------------------------------------------
"""
Class:  Rgvd(mean,std,positive=1)

     Description of a number that will be used to generate a Gaussian random distribution with a
     mean and standard deviation.

        mean     - mean value
        std      - standard distribution
        positive - keep generating if not positive (=1) or allow negative value (=0).

"""
class Rgvd:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,mean,std,positive):

        self.mean = mean
        self.std = std
        self.positive = positive
        
    #-----------------------------------------------------------------------------------------------
    # summary as a string
    #-----------------------------------------------------------------------------------------------
    def summary(self):
        return "V:%f+-%f"%(self.mean,self.std)
        
    #-----------------------------------------------------------------------------------------------
    # get the next random number
    #-----------------------------------------------------------------------------------------------
    def next(self):
        rg = 0
        active = True
        while active:
            rg = numpy.random.normal(self.mean, self.std, 1)
            if self.positive:
                if rg<0:
                    break
            active = False
            
        return rg

#---------------------------------------------------------------------------------------------------
"""
Class:  Pathogen(avg_duration,pi_initial,pi_decay,death_rate)

     Description of a pathogen properties in an outbreak.

        avg_duration - average duration of the desease
        pi_initial   - initial infection probability on exposure
        pi_decay     - decay of infection probability per day
        death_rate   - rate of death when infected

"""
class Pathogen:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,avg_duration,pi_initial,pi_decay,death_rate):
        self.avg_duration = avg_duration
        self.pi_initial = pi_initial
        self.pi_decay = pi_decay
        self.death_rate = death_rate
        
    def pi(self,t):
        return self.pi_initial*numpy.exp(t*self.pi_decay)
    
    def expose(self,i_day):
        return numpy.random.uniform()<self.pi(i_day)
    
    def duration(self):
        return self.avg_duration.next()
        
    def summary(self):
        return "AvgDuration: %f +- %f, P_infect: %f,%f Death_rate: %f"%\
            (self.avg_duration.mean,self.avg_duration.std,\
             self.pi_initial,self.pi_decay,self.death_rate)

#---------------------------------------------------------------------------------------------------
"""
Class:  Population(ntotal)

     Description of a general population with a given number of nodes.

        ntotal - total number of people to consider.

"""
class Population:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self):
        self.list = []
        self.infected = []
        self.recovered = []
        self.deceased = []

    def add_person(self,person):
        self.list.append(person)
        return

    def infect(self,id,corona):
        # person
        p = self.list[id]
        # was removed?
        if p.status == -1:
            self.recovered.remove(id)
        if p.status == -2:
            self.deceased.remove(id)
        # infect and add to infected list
        p.infect(corona.duration())
        self.infected.append(id)

    def expose(self,id,corona):
        # person
        p = self.list[id]
        
        # is susceptible?
        if p.status != 0:
            return

        # expose the person
        if not corona.expose(p.n_days_i):
            return
        
        # infect and add to infected list
        p.infect(corona.duration())
        self.infected.append(id)
        
        return
    
    def spread(self,corona):

        # loop through infected people once
        for id in self.infected:
            p = self.list[id]
            n_contact_today = int(p.social_type.avg_contact.next())
            for i in range(1,n_contact_today):
                iid = (id + numpy.random.randint(0,p.social_type.n_family)) % (self.n())
                # expose this person
                self.expose(iid,corona)

            # increase number of days sick
            p.next_day()
            # remove person from our list
            if p.n_days_i>p.n_days_r:
                self.infected.remove(id)
                # die or recover
                if numpy.random.uniform(0,1) > corona.death_rate:
                    p.recover(corona)
                    self.recovered.append(id)
                else:
                    p.die(corona)
                    self.deceased.append(id)
        return
    
    def i(self):
        return len(self.infected)

    def n(self):
        return len(self.list)

    def r(self):
        return len(self.recovered)

    def d(self):
        return len(self.deceased)

    def show(self):
        print "##\n Population of %d people (infected: %d)"%(self.n(),self.i())
        for p in self.list:
            p.show()

    def summary(self):
        return " Population: n=%d, n_infected=%d, n_recovered=%d, n_deceased: %d"%\
            (self.n(),self.i(),self.r(),self.d())
            
#---------------------------------------------------------------------------------------------------
"""
Class:  Social_type(avg_contact, n_family, n_work, ratio_family)

     Description of a social tpye relevant to the description of a population and their social
     behaviour.

        avg_contact  - number of average contacts per day (mean and std)
        n_family     - number of family members
        n_work       - number of work colleages
        ratio_family - ratio of contact with family (0.1 -> 10% of contacts with family, rest work)

"""
class Social_type:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,avg_contact,n_family,n_work,ratio_family=1):

        self.avg_contact = avg_contact
        self.n_family = n_family
        self.n_work = n_work
        self.ratio_family = ratio_family
        
    #-----------------------------------------------------------------------------------------------
    # Return string of social type.
    #-----------------------------------------------------------------------------------------------
    def summary(self):
        return " C:%s, NF:%d, NW:%d, RF:%f"%\
            (self.avg_contact.summary(),self.n_family,self.n_work,self.ratio_family)

#---------------------------------------------------------------------------------------------------
"""
Class:  Person(id, social_type, status=0, n_days_i=0, n_days_r=0)

     Description of a node in an infectuous disease simulation.

        id          - index from generation
        social_type - defines the social behaviour of the person
        status      - -2 deceased
                      -1 recovered, not susceptible
                       0 susceptible
                       1 infected
        n_days_i    - number of days infected
        n_days_r    - days infection lasts

"""
class Person:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,id,social_type,status=0,n_days_i=0,n_days_r=0):
        self.id = id
        self.social_type = social_type
        self.status = status
        self.n_days_i = n_days_i
        self.n_days_r = n_days_r
        
    #-----------------------------------------------------------------------------------------------
    # Infect the person, which is saying person is infected and determine when completed
    #-----------------------------------------------------------------------------------------------
    def infect(self,duration):
        self.status = 1
        self.n_days_i = 1
        self.n_days_r = duration
        return

    #-----------------------------------------------------------------------------------------------
    # Recover person (depending on the death rate of the pathogen
    #-----------------------------------------------------------------------------------------------
    def recover(self,pathogen):
        self.status = -1
        self.n_days_i = 0
        self.n_days_r = 0
        return

    #-----------------------------------------------------------------------------------------------
    # Recover person (depending on the death rate of the pathogen
    #-----------------------------------------------------------------------------------------------
    def die(self,pathogen):
        self.status = -2
        self.n_days_i = 0
        self.n_days_r = 0
        return

    #-----------------------------------------------------------------------------------------------
    # Next day propagates person into the next day (recovery/death is not our responsiblity)
    #-----------------------------------------------------------------------------------------------
    def next_day(self):
        if self.status>0:
            self.n_days_i += 1
        return

    #-----------------------------------------------------------------------------------------------
    # Show what we have
    #-----------------------------------------------------------------------------------------------
    def show(self):
        print " Person: %7d - [%s] (%d, %d, %d)"%\
            (self.id,self.social_type.summary(),self.status,self.n_days_i,self.n_days_r)
        return

#===================================================================================================
# MAIN
#===================================================================================================
# Define string to explain usage of the script
usage  = "\nUsage: outbreak.py [ --n_popul=<int> --i_initial=<int> --n_day_max=<int> \
                                 --reco_mean=<float> --reco_std=<float> --pi_inital=<float> --pi_decay=<float> \
                                 --death_rate=<float> --exposure_avg=<float> exposure_std=<float> \
                                 --seed=<int> --record=<string> --date=<string>]\n"

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

# input parameters for the SIR modelling
N_POPULATION = 6883000
N_DAYS = 20
I_INITIAL = 6620
RECO_MEAN = 30
RECO_STD = 8
PI_INITIAL = 0.06
PI_DECAY = 0.10
DEATH_RATE = 0.04
EXPOSURE_AVG = 5
EXPOSURE_STD = 2
SEED = 1000
RECORD = "data/time_series_covid19"
DATE = "2020-03-31"

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

corona = Pathogen(Rgvd(RECO_MEAN,RECO_STD,1),PI_INITIAL,PI_DECAY,DEATH_RATE)
social_type = Social_type(Rgvd(EXPOSURE_AVG,EXPOSURE_STD,1),100,20,0.5)
numpy.random.seed(seed=int(SEED))

# Generate the population

id = 0
popul = Population()

while (popul.n()<N_POPULATION):
    p = Person(id,social_type)
    popul.add_person(p)

    id += 1 # increase index for the next person
print "Day: %d  == %s"%(-1, popul.summary())

# Generate an infection
n = popul.n()
while (popul.i() < I_INITIAL):

    id = numpy.random.randint(0,n)
    popul.infect(id,corona)
print "Day: %d == %s"%(0, popul.summary()
)
# propagate our spreading model
i_days = 0
history = History(RECORD)
today = date_s
print " Corona virus: %s"%(corona.summary())
while (i_days<N_DAYS):

    history.add_day(today,len(popul.infected),len(popul.recovered),len(popul.deceased))
    print "Day: %d (%s) == %s"%(i_days, today, popul.summary())
    
    popul.spread(corona)

    # increase the day
    i_days += 1
    today = today + datetime.timedelta(days=1)

    # check population status
    if popul.r()>=popul.n():
        print "Day: %d (%s) == %s"%(i_days, today, popul.summary())
        print ""
        print " ==================="
        print " Pathogen completed!"
        print " ==================="
        print " - duration %d days"%(i_days) 
        print " - colletaral %s"%(popul.summary()) 
        print ""
        break
        
    # check pathogen status
    if popul.i()<1:
        print "Day: %d (%s) == %s"%(i_days, today, popul.summary())
        print ""
        print " ====================="
        print " The pathogen is dead!"
        print " ====================="
        print " - duration %d days"%(i_days) 
        print " - colletaral %s"%(popul.summary()) 
        print ""
        break


print "Day: %d (%s) == %s"%(i_days, today, popul.summary())

history.write()
