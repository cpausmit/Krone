import numpy

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
