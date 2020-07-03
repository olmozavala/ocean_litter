#!/bin/bash

start_date_str="2010-01-01"
end_date_str="2010-01-06"
output_path="/home/data/UN_Litter_data/output"
run_name="TEST"
inc_per_run=1

t=0
c_start_date=$(date --date="${start_date_str} +$((t)) days")
c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days +%Y-%m-%d")
end_date=$(date --date="${end_date_str}")

c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
end_date_sec=$(date --date="${end_date_str}" "+%s")

while [ $c_start_date_sec -lt $end_date_sec ]
do
  prev_start_date=$c_start_date
  prev_end_date=$c_end_date
  echo "====================== NEW RUN t=$t ================================"
  if [ $t -eq  0 ]
  then
    cmd="mpirun -np 8 python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False ${run_name}_${c_start_date}_${c_end_date}"
  else
    cmd="mpirun -np 8 python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
  fi
  echo $cmd
  `$cmd > 'CurrentRun.log'`
  t=$[$t+$inc_per_run]
  c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
  c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
  c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
done


# start_date=2010-01-01:0  end_date=2010-01-04:0 winds=True diff=True unbeaching=True name=DELETE useRestart=True
#mpirun -np 8 python 0_WorldLitter.py 2010-01-01:0 2015-01-01:0 False True False NoWinds_YesDiff_2010_01 True 30 > Running.log &
#mpirun -np 8 python 0_WorldLitter.py 2010-12-27:0 2015-01-01:0 False True False NoWinds_YesDiff_2010_01 /data/UN_Litter_data/output/NoWinds_YesDiff_2010_01_2010-11-27_2010-12-27.nc 30 > Running.log &

# start_date=2010-01-01:0  end_date=2010-01-04:0 unbeaching=True name=DELETE
#mpirun -np 8 python 1_MergeRuns.py 2010-01-01:0 2015-01-01:0 False NoWinds_YesDiff_2010_01 30 > Merging.log &
