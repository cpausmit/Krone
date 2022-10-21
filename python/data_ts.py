#---------------------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------------------
import csv
import sys,os

#---------------------------------------------------------------------------------------------------
"""
Class:  Data_ts()

     Description of the relevant history of the outbreak of an infectious disease.

       nadd         - number of intervals (days) added together
       dates        - times series dates (list)
       population   - population of quoted country or state
       infected     - number of infected people per day (list)
       infected_day - number of infected people per day (list)
       deceased     - number of deceased people per day (list)
       deceased_day - number of deceased people per day (list)

"""
class Data_ts:

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,data_dir="data"):
        self.web_site = "https://raw.githubusercontent.com"
        self.web_dir = "CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"
        self.input_files_infected = [
            "time_series_covid19_confirmed_global.csv",
            "time_series_covid19_confirmed_US.csv"
        ]
        self.input_files_deceased = [
            "time_series_covid19_deaths_global.csv",
            "time_series_covid19_deaths_US.csv"
        ]
#        input_files_mc = [
#            "time_series_covid19_confirmed_SIMUS.csv",
#            "time_series_covid19_deaths_SIMUS.csv"
#        ]

        self.nadd = 1
        self.data_dir = data_dir
        self.times = []
        self.population = {}
        self.infected = {}
        self.deceased = {}
        
    #-----------------------------------------------------------------------------------------------
    # summary as a string
    #-----------------------------------------------------------------------------------------------
    def summary(self):
        range = " Data_ts: EMPTY"
        if len(self.times)>0:
            range = " Data_ts: %s -> %s"%(self.times[0],self.times[-1])
        return range
        
    #-----------------------------------------------------------------------------------------------
    # download new version of the files
    #-----------------------------------------------------------------------------------------------
    def update_files(self,quiet=False):
        if not quiet:
            print(" Update the data files")
        for f in self.input_files_infected+self.input_files_deceased:
            cmd = "wget %s/%s/%s -O %s/%s >& /dev/null"\
                %(self.web_site,self.web_dir,f,self.data_dir,f)
            if not quiet:
                print(" Updating: %s"%(cmd))
            os.system(cmd)
        return

    #-----------------------------------------------------------------------------------------------
    # load all data files
    #-----------------------------------------------------------------------------------------------
    def load_data(self,quiet=False):
        if not quiet:
            print(" Load all data from files")
        for f in self.input_files_infected:
            self.read_file(f,self.infected,self.population,quiet)
        for f in self.input_files_deceased:
            self.read_file(f,self.deceased,self.population,quiet)
            
        self.read_file_pop("populations.csv",self.population,quiet)
            
        return

    #-----------------------------------------------------------------------------------------------
    # identify the data file format for proper reading
    #-----------------------------------------------------------------------------------------------
    def find_format(self,header):
        # determine format
        if 'UID' in header[0:2]: # this is US format
            n_offset = 11
            n_tag = 6
        else:
            n_offset = 4
            n_tag = 1
        return n_tag,n_offset
    
    #-----------------------------------------------------------------------------------------------
    # load one file
    #-----------------------------------------------------------------------------------------------
    def read_file(self,data_file,values,population,quiet=False):
        if not quiet:
            print(" Reading the data -- from: %s"%data_file)
        # loop the file
        with open("%s/%s"%(self.data_dir,data_file),'r') as csvfile:
            ts_file = csv.reader(csvfile, delimiter=',')
            first = True
            pop_local = {}
            n_population = -1
            for row in ts_file:
                if first:
                    first = False
                    n_tag, n_offset = self.find_format(row)
                    tmp = row[n_offset:]
                    # for whatever reason the 'death' file also includes a column with population?!
                    if 'Population' in tmp[0]:
                        n_population = n_offset
                        n_offset += 1
                        tmp = row[n_offset:]
                    if len(self.times) == 0:
                        # take those times
                        self.times = tmp
                    else:
                        # check consistency
                        if len(tmp) != len(self.times):
                            print(" ERROR - found inconsistent time series length (O:%d != N:%d)"%\
                                  (len(self.times),len(tmp)))
                            sys.exit(-1)
                        if tmp[0] != self.times[0]:
                            print(" ERROR - found inconsistent time series start (O:%s != N:%s)"%\
                                  (tmp[0],self.times[0]))
                            sys.exit(-1)
                    continue
                
                # read this line as the next timeseries values, might have to be added to existing
                tag = row[n_tag]
    
                # find existing series or create empty one
                if tag in values.keys():
                    series = values[tag]
                else:
                    series = [ 0 ] * len(self.times)
                    
                # loop through the values and convert to integer
                tmp_values = []
                for value in row[n_offset:]:
                    tmp_values.append(int(value))
    
                series = [x+y for x,y in zip(series,tmp_values)]
    
                values[tag] = series
                if n_population != -1:
                    if tag in population:
                        population[tag] += int(row[n_population])
                    else:
                        population[tag] = int(row[n_population])                        
                
        return
    
    #-----------------------------------------------------------------------------------------------
    # load external population file
    #-----------------------------------------------------------------------------------------------
    def read_file_pop(self,data_file,population,quiet=False):
        if not quiet:
            print(" Reading the population data -- from: %s"%data_file)
        # loop the file
        with open("%s/%s"%(self.data_dir,data_file),'r') as csvfile:
            ts_file = csv.reader(csvfile, delimiter=',')
            for row in ts_file:
                print(row)
                if len(row) > 0 and not row[0].startswith('#'):
                    tag = row[1].strip()
                    n = int(row[2].replace(' ',''))
                    population[tag] = n
        return

    #-----------------------------------------------------------------------------------------------
    # combine data from several days
    #-----------------------------------------------------------------------------------------------
    def combine_values(self,nadd=7):

        self.nadd = nadd
        
        # temporary combined variables
        tim = []

        # first sort of the dates to use
        n = 0
        for t in reversed(self.times):
            if n%nadd == 0:
                tim.append(t)
            n += 1
        self.times = tim[::-1]

        # now add up the numbers for each tag separately
        for tag in self.infected:
            inf = []
            dec = []
            n = 0
            for i,d in zip(self.infected[tag][::-1],self.deceased[tag][::-1]):
                if n%nadd == 0:
                    inf.append(i)
                    dec.append(d)
                n += 1

            self.infected[tag] = inf[::-1]
            self.deceased[tag] = dec[::-1]
            
        return

    def rolling_values(self,nroll=7):

        if nroll < 2:
            return
        
        for tag in self.infected:
            inf_csum, infs = [0], []
            #dec_csum, decs = [0], []
            for i, x in enumerate(self.infected[tag]):
                #print(i,tag,len(self.infected[tag]),len(self.deceased[tag]),dec_csum)
                inf_csum.append(inf_csum[i-1] + self.infected[tag][i])
                #dec_csum.append(dec_csum[i-1] + self.deceased[tag][i])
                if i>=nroll:
                    inf = (inf_csum[i] - inf_csum[i-nroll])/float(nroll)
                    #dec = (dec_csum[i] - dec_csum[i-nroll])/float(nroll)
                else:
                    inf = (inf_csum[i] - inf_csum[0])/float(i+1)
                    #dec = (dec_csum[i] - dec_csum[0])/float(i+1)

                infs.append(inf)
                #decs.append(dec)
            
            self.infected[tag] = infs
            #self.deceased[tag] = decs
            
