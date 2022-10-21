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
