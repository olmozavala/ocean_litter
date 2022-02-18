#!/bin/bash

# This code generates multiple bash files from generalrun_[coaps|hpc]  and runs them in parallel.
# Each bash file is a single monthly release

# Iterate years
for j in {1..20..1}
#for j in {20..20..1}
do
    cur_year=$(printf "%02d" $j)
    # Iterate Months
    for i in {1..12..1}
    do
        cur_month=$(printf "%02d" $i)
        echo 'Finishing year for Year: 20'${cur_year} 'Month:'${cur_month}
        # ----------- For HPC running extra years------------
        #sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" generalrun_hpc_extra_year.sh > run20${cur_year}_${cur_month}.sh
        # ----------- For HPC starting new run ------------
        sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" generalrun_hpc.sh > run20${cur_year}_${cur_month}.sh
        sbatch run20${cur_year}_${cur_month}.sh
    done
done
