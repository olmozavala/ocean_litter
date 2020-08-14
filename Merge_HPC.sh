#!/bin/bash

start_date_str="2014-12-02"
end_date_str="2020-01-01"
inc_per_run=30

# Iterate years
for j in {10..14..1}
do
    cur_year=$(printf "%02d" $j)
    # Iterate Months
    for i in {1..12..1}
    do
        cur_month=$(printf "%02d" $i)
        run_name="TenYears_YesWinds_YesDiffusion_NoUnbeaching_20${cur_year}_${cur_month}"
        cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
        echo $cmd
        #`$cmd > 'Merge_20YEAR_MONTH.log'`
    done
done
