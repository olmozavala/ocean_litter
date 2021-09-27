#!/bin/bash

start_date_str="20YEAR-MONTH-01"
end_date_str="2020-01-01"
output_path="/data/UN_Litter_data/output"
run_name="Continue_YesWinds_YesDiffusion_NoUnbeaching_20YEAR_MONTH"
inc_per_run=30
proc=16

t=0
c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
end_date=$(date --date="${end_date_str}")

c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
end_date_sec=$(date --date="${end_date_str}" "+%s")

c_end_date_sec=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%s")
if [ $c_end_date_sec -lt $end_date_sec ]
then
  c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
else
  c_end_date=$(date --date="${end_date_str}" "+%Y-%m-%d")
fi

while [ $c_start_date_sec -lt $end_date_sec ]
do
  echo "====================== NEW RUN t=$t ================================"
  if [ $t -eq  0 ]
  then
    # In this case it is only running inc_per_run days normally
    cmd="mpirun -np ${proc} python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False $run_name /data/UN_Litter_data/output/YesWinds_YesDiffusion_NoUnbeaching/YesWinds_YesDiffusion_NoUnbeaching_2010_MONTH.nc $inc_per_run"
  else
    # In this case it should start from the previous coordinates
    cmd="mpirun -np ${proc} python  0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
  fi
  echo $cmd
  `$cmd > 'CurrentRun20YEAR_MONTH.log'`
  t=$[$t+$inc_per_run]
  prev_start_date=$c_start_date
  prev_end_date=$c_end_date
  c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
  c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
  c_end_date_sec=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%s")
  if [ $c_end_date_sec -lt $end_date_sec ]
  then
      c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
  else
      c_end_date=$(date --date="${end_date_str}" "+%Y-%m-%d")
  fi
done

#cmd="python 2_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
#echo $cmd
#`$cmd > 'Merge_20YEAR_MONTH.log'`

#cmd="rm  ${output_path}/${run_name}_*"
#echo $cmd
#`$cmd`
#
# These are the 'temporal' folders from OP
#cmd="rm -rf ${output_path}/out-*"
#echo $cmd
#`$cmd`

