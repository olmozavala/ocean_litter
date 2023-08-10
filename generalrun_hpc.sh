#!/bin/bash

#SBATCH --job-name="20YEAR_MONTH"
#SBATCH -t 20:00:00
#SBATCH -p coaps_q
##SBATCH -p genacc_q
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --mem=64G
#SBATCH --mail-type=END,FAIL
##SBATCH --mail-type=ALL

module load intel openmpi
module load anaconda/3.7.3

start_date_str="20YEAR-MONTH-01"
end_date_str="2023-01-01"
output_path="/gpfs/home/osz09/scratch/output_2022"
run_name="UpToDec2022_YesWinds_YesDiffusion_NoUnbeaching_20YEAR_MONTH"
inc_per_run=30

t=0
c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
end_date=$(date --date="${end_date_str}")

c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
end_date_sec=$(date --date="${end_date_str}" "+%s")

c_end_date_sec=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%s")

# Here it decides if the next end date is the final END DATE or CURRENT DATE + increment
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
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False ${run_name}_${c_start_date}_${c_end_date}"
    # cmd="srun /gpfs/home/osz09/.conda/envs/parcels_mpi/bin/python 1_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False ${run_name}_${c_start_date}_${c_end_date}"
  else
    # In this case it should start from the previous coordinates
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
    # cmd="srun /gpfs/home/osz09/.conda/envs/parcels_mpi/bin/python 1_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
  fi
  echo $cmd
  `$cmd > 'CurrentRun20YEAR_MONTH.log'`
  t=$[$t+$inc_per_run]
  prev_start_date=$c_start_date
  prev_end_date=$c_end_date
  c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
  c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
  c_end_date_sec=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%s")
  # Here it decides if the next end date is the final END DATE or CURRENT DATE + increment
  if [ $c_end_date_sec -lt $end_date_sec ]
  then
      c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
  else
      c_end_date=$(date --date="${end_date_str}" "+%Y-%m-%d")
  fi
done

# # This part of the code merges all the intermediate runs into a single netCDF
# cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 2_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
# echo $cmd
# `$cmd > 'Merge_20YEAR_MONTH.log'`

# Here we remove all the intermediate netcdf files
#cmd="rm  ${output_path}/${run_name}_*"
#echo $cmd
#`$cmd`

# Removes any folders left from Ocean Parcels
# These are the 'temporal' folders from OP
#cmd="rm -rf ${output_path}/out-*"
#echo $cmd
#`$cmd`

