import numpy

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
