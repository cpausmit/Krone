Krone - Corona Virus (COVID-19) Data Analysis
=============================================


Installation
------------

For installation please go to a place where you can find it back easily and proceed:

* git clone https://github.com/cpausmit/Krone.git
* sudo dnf install python-pandas python-numpy python-matplotlib
* cd Krone
* source ./setup.sh

Run
---

Number of new infected (delta) per day with the last day being 2020-04-07

    ./c19.py --update --tags="China,US,Italy,Germany,France,Spain" --delta --tmax=2020-04-07

Number of new deaths with the last day being 2020-04-07, cut at 500 maximum

    ./c19.py --update --tags="China,US,Italy,Germany,France,Spain" --death --vmax=500

US data analysis of the New England states, Number of new infected per day, starting 2020-02-12 

    ./c19.py --update --us --tags='Vermont,New Hampshire,Maine,Massachusetts,Connecticut,Rhode Island' --tmin 2020-02-12  --delta

Population percentage of new infected over 7 day averages, starting March 15

    ./c19.py --update --tags='Illinois,Massachusetts,Switzerland' --delta --combine 7 --relative --tmin 2020-03-15

Run a full outbreak simulation for MA and plot it comparing to the data from JHU. The outbreak.py script has a ton of parameters to tune the simulation. The gyst of such a comparison is given below:

  ./outbreak.py --pi_initial=0.0295;./covid-19_data.py --tmin 2020-03-10 --tmax 2020-04-20 --us --tags="Massachusetts" --mc

Etc.

Improvements on the Way
-----------------------

The simulation can be extended significantly to more accurately represent the details of what is going on. The simulation will of course never be perfect but you can study the effect of very well controlled canges to the model and make reasonably accurate predictions if it does not go to far into the future.

There are a few things I am trying to implement in the not to distant future.

* add age to each person
* implement a population that matches the profile of the dataset in terms of
   * age profile
   * number of members in the household (family) and at the workplace
   * visits to the environment beyond family and work
* store generated population to disc and make them restorable from disk
* make population status storeable to disk
* develop tools to plot properties of the given population situation

* expand ability to read the JHU data and generate populations for each dataset

* calculate probability of data/MC comparidon as a function of a given parameter and determine the minimum
