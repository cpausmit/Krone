import numpy

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

            contact_delta_indices = p.social_type.daily_exposure()
            for did in contact_delta_indices:
                iid = (id + did) % (self.n())
                # expose this person
                self.expose(iid,corona)
                
            #n_contact_today = int(p.social_type.avg_contact.next())
            #for i in range(1,n_contact_today):
            #    iid = (id + numpy.random.randint(0,p.social_type.n_family)) % (self.n())
            #    # expose this person
            #    self.expose(iid,corona)

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

    def is_active(self,today,i_days):
        status = True

        # check population status
        if self.r()>=self.n():
            print "Day: %d (%s) == %s"%(i_days, today, self.summary())
            print ""
            print " ==================="
            print " Pathogen completed!"
            print " ==================="
            print " - duration %d days"%(i_days) 
            print " - colletaral %s"%(self.summary()) 
            print ""
            status = False
            
        # check pathogen status
        if self.i()<1:
            print "Day: %d (%s) == %s"%(i_days, today, self.summary())
            print ""
            print " ====================="
            print " The pathogen is dead!"
            print " ====================="
            print " - duration %d days"%(i_days) 
            print " - colletaral %s"%(self.summary()) 
            print ""
            status = False

        return status
    
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

    #-----------------------------------------------------------------------------------------------
    # Return string of social type.
    #-----------------------------------------------------------------------------------------------
    def daily_exposure(self):
        ids = []

        # how many encounters today?
        nc = int(self.avg_contact.next())
        
        # now throw the indices for the encounters
        for i in range(0,nc):
            # determine family or work
            if numpy.random.uniform()<self.ratio_family:
                ids.append(numpy.random.randint(0,self.n_family))
            else:
                ids.append(numpy.random.randint(0,self.n_work))

        return ids

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
    # Is the spreading complete? No more infected or all removed.
    #-----------------------------------------------------------------------------------------------
    def is_done(self,today,i_days):
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
            return True
            
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
            return True

        return False
    
    #-----------------------------------------------------------------------------------------------
    # Show what we have
    #-----------------------------------------------------------------------------------------------
    def show(self):
        print " Person: %7d - [%s] (%d, %d, %d)"%\
            (self.id,self.social_type.summary(),self.status,self.n_days_i,self.n_days_r)
        return
