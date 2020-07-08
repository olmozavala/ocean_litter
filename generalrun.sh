#!/bin/bash

#SBATCH --job-name="20YEAR_MONTH"
#SBATCH -t  300:00:00
#SBATCH -p coaps_q
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --mem=128G
#SBATCH --mail-type=FAIL

module load intel-openmpi
module load anaconda3.7.3

#srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py '20YEAR-MONTH-01:0' '2015-01-01:0' True False False 'YesWinds_NoDiffusion_20YEAR_MONTH' True 30 > YesWinds_NoDiffusion_20YEAR_MONTH.log
#srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py '20YEAR-MONTH-01:0' '2015-01-01:0' False True False 'Single_Release_FiveYears_EachMonth_NoWinds_WithDiffusion_20YEAR_MONTH' True 30 > Single_Release_FiveYears_EachMonth_NoWinds_WithDiffusion_20YEAR_MONTH.log
#srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py '20YEAR-MONTH-01:0' '2015-01-01:0' True False False 'Single_Release_FiveYears_EachMonth_WithWinds_NoDiffusion_20YEAR_MONTH' True 30 > Single_Release_FiveYears_EachMonth_WithWinds_NoDiffusion_20YEAR_MONTH.log

start_date_str="20YEAR-MONTH-01"
end_date_str="2015-01-01"
output_path="/home/data/UN_Litter_data/output"
run_name="YesWind_YesDiffusion_20YEAR_MONTH"
inc_per_run=30

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
    #cmd="mpirun -np 8 python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False ${run_name}_${c_start_date}_${c_end_date}"
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False ${run_name}_${c_start_date}_${c_end_date}"
  else
    #cmd="mpirun -np 8 python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True False False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
    cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False $run_name $output_path/${run_name}_${prev_start_date}_${prev_end_date}.nc $inc_per_run"
  fi
  echo $cmd
  `$cmd > 'CurrentRun20YEAR_MONTH.log'`
  t=$[$t+$inc_per_run]
  c_start_date_sec=$(date --date="${start_date_str} +$((t)) days" "+%s")
  c_start_date=$(date --date="${start_date_str} +$((t)) days" "+%Y-%m-%d")
  c_end_date=$(date --date="${start_date_str} +$((t+inc_per_run)) days" "+%Y-%m-%d")
done

# start_date=2010-01-01:0  end_date=2010-01-04:0 unbeaching=True name=DELETE
#mpirun -np 8 python 1_MergeRuns.py 2010-01-01:0 2015-01-01:0 False NoWinds_YesDiff_2010_01 30 > Merging.log &

cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
echo $cmd
`$cmd > 'Merge_20YEAR_MONTH.log'`

cmd="rm  ${output_path}/${run_name}_*"
echo $cmd
`$cmd`

