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
end_date_str="2014-01-06"
output_path="/gpfs/home/osz09/scratch/output/"
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
  echo "====================== NEW RUN t=$t ================================"
  if [ $t -eq  0 ]
  then
    #cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 False True False  ${run_name}_${c_start_date}_${c_end_date}"
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False  ${run_name}_${c_start_date}_${c_end_date}"
  else
    #cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 False True False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
  fi
  echo $cmd
  `$cmd > "${run_name}.log"`
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


cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
echo $cmd
`$cmd`

