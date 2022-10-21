#---------------------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
"""
Class:  Parameter()

     Parameter description used for modelling.

       name      - short name tag, need to keep unique to distinguish in dictionary
       plot_name - axis label type of description
       value     - parameter value
       std       - parameter standard deviation
       min       - minimum value
       max       - maximum value

"""
class Parameter:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,name,plot_name,value,std=0,min=0,max=0):
        self.name = name
        self.plot_name = plot_name
        self.value = value
        self.std = std
        self.min = min
        self.max = max
        
    #-----------------------------------------------------------------------------------------------
    # summary as a string
    #-----------------------------------------------------------------------------------------------
    def summary(self):
        return " %s: %f +- %f [%f,%f] -- %s"%\
            (self.name,self.value,self.std,self.min,self.max,self.plot_name)

    #-----------------------------------------------------------------------------------------------
    # range
    #-----------------------------------------------------------------------------------------------
    def range(self):
        return self.min,self.max

    #-----------------------------------------------------------------------------------------------
    # set range
    #-----------------------------------------------------------------------------------------------
    def set_range(self,min,max):
        self.min = min
        self.max = max
        return
        
