#!/bin/bash

#SBATCH --job-name="OP 2010"
#SBATCH -t  300:00:00
#SBATCH -p coaps_q
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --mem=128G
#SBATCH --mail-type=FAIL

module load intel openmpi

start_date_str="2010-01-01"
end_date_str="2014-01-06"
output_path="/gpfs/home/osz09/scratch/globaldebrisoutput/"
run_name="YesWinds_NoDiffusion_2010_01"
inc_per_run=30

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
    cur_year=$(printf "%02d" $j)
    # Iterate Months
    for i in {1..12..1}
    do
        cur_month=$(printf "%02d" $i)
        echo 'Year: 20'${cur_year} 'Month:'${cur_month}
        sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" generalrun_hpc.sh > run20${cur_year}_${cur_month}.sh
        sbatch run20${cur_year}_${cur_month}.sh
    done
done
