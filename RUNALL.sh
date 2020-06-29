#!/bin/bash

# start_date=2010-01-01:0  end_date=2010-01-04:0 winds=True diff=True unbeaching=True name=DELETE useRestart=True
#mpirun -np 8 python 0_WorldLitter.py 2010-01-01:0 2015-01-01:0 False True False Single_Release_FiveYears_2010_01_NoWinds_WithDiff True 30
#mpirun -np 8 python 0_WorldLitter.py 2010-11-27:0 2015-01-01:0 False True False Single_Release_FiveYears_2010_01_NoWinds_WithDiff /data/UN_Litter_data/output/Single_Release_FiveYears_2010_01_NoWinds_WithDiff_2010-10-28_2010-11-27__10.nc 30
mpirun -np 8 python 0_WorldLitter.py 2012-08-18:0 2015-01-01:0 False True False Single_Release_FiveYears_2010_01_NoWinds_WithDiff /data/UN_Litter_data/output/Single_Release_FiveYears_2010_01_NoWinds_WithDiff_2011-09-23_2012-08-18__10.nc 30
# start_date=2010-01-01:0  end_date=2010-01-04:0 unbeaching=True name=DELETE
mpirun -np 8 python 1_MergeRuns.py 2010-01-01:0 2015-01-01:0 False Single_Release_FiveYears_2010_01_NoWinds_WithDiff 30
