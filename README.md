Krone - Corona Virus (COVID-19) Data Analysis
=============================================


Installation
------------

For installation please go to a place where you can find it back easily and proceed:

* git clone https://github.com/cpausmit/Krone.git
* sudo dnf install python-pandas python-numpy python-matplotlib

Run
---

Number of new infected (delta) per day with the last day being 2020-04-07

  ./covid-19_data.py --tags="China,US,Italy,Germany,France,Spain" --delta --tmax=2020-04-07

Number of new deaths with the last day being 2020-04-07, cut at 500 maximum

  ./covid-19_data.py --tags="China,US,Italy,Germany,France,Spain" --death --vmax=500

Etc.