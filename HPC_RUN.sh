#!/bin/bash

#SBATCH --job-name="OP 2010"
#SBATCH -t  300:00:00
#SBATCH -p coaps_q
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --mem=128G
#SBATCH --mail-type=FAIL

module load intel-openmpi
module load anaconda3.7.3

start_date_str="2010-01-01"
end_date_str="2010-01-06"
output_path="/gpfs/home/osz09/scratch/output/"
run_name="NoWinds_YesDiffusion_2010_01_NoSplit"
inc_per_run=1

t=0
c_start_date=$(date --date="${start_date_str} +$((t)) days")
c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days +%Y-%m-%d:0")
end_date=$(date --date="${end_date_str}")

c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
end_date_sec=$(date --date="${end_date_str}" "+%s")

while [ $c_start_date_sec -lt $end_date_sec ]
do
  prev_start_date=$c_start_date
  prev_end_date=$c_end_date
  c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")

  c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
  c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
  echo "======================="
  echo $c_start_date
  echo $c_end_date
  echo $c_start_date_sec
  if [ $t -eq  0 ]
  then
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 False True False $run_name > ${run_name}.log"
  else
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run > ${run_name}.log"
  fi
  echo $cmd
  `$cmd`
  t=$[$t+inc_per_run]
done

#srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py '2011-04-26:0' '2015-01-01:0' True False False 'YesWinds_NoDiffusion_2010_01' '/gpfs/home/osz09/scratch/output/YesWinds_NoDiffusion_2010_01_2011-03-27_2011-04-26.nc' 30 > YesWinds_NoDiffusion_2010_01.log
