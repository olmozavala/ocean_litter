#!/bin/bash

#SBATCH --job-name="OP 2010"
#SBATCH -t  300:00:00
#SBATCH -p coaps_q
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=128G
#SBATCH --mail-type=FAIL

module load intel-openmpi
module load anaconda3.7.3

start_date_str="2010-01-01"
end_date_str="2015-01-01"
output_path="/gpfs/home/osz09/scratch/output/"
run_name="YesWinds_NoDiffusion_2010_01"
#run_name="NoWinds_YesDiffusion_2010_01"
inc_per_run=30

cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
echo $cmd
`$cmd > "Merge_${run_name}.log"`

#cmd="rm  ${output_path}/${run_name}_*"
#echo $cmd
#`$cmd`

