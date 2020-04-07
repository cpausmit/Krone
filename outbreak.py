#!/usr/bin/env python
import sys,os

initial = 213
exp = 2
n_days = 30

if len(sys.argv)>1:
    initial = int(sys.argv[1])
if len(sys.argv)>2:
    exp = float(sys.argv[2])
if len(sys.argv)>3:
    n_days = int(sys.argv[3])

n = initial
day = 0
while day < n_days:
    n = n * exp
    print " Day %3d: %e"%(day,float(n))
    day += 1

