#!/bin/bash

# Iterate years
for j in {14..14..1}
do
    cur_year=$(printf "%02d" $j)
    # Iterate Months
    for i in {6..6..1}
    do
        cur_month=$(printf "%02d" $i)
        echo 'Year: 20'${cur_year} 'Month:'${cur_month}
        sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" generalrun.sh > run20${cur_year}_${cur_month}.sh
        sbatch run20${cur_year}_${cur_month}.sh
    done
done
