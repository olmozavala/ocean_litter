#!/bin/bash

# start_date=2010-01-01:0  end_date=2010-01-04:0 winds=True diff=True unbeaching=True name=DELETE useRestart=True
mpirun -np 8 python 0_WorldLitter.py 2010-01-01:0 2015-01-01:0 False True False NoWinds_YesDiff_2010_01 True 30 > Running.log &

# start_date=2010-01-01:0  end_date=2010-01-04:0 unbeaching=True name=DELETE
#mpirun -np 8 python 1_MergeRuns.py 2010-01-01:0 2015-01-01:0 False NoWinds_YesDiff_2010_01 30 > Merging.log &
