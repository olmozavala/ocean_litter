#!/bin/bash
  
#SBATCH --job-name="MergeAll"
#SBATCH -t 3:00:00            
#SBATCH -p coaps_q
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem=32G
#SBATCH --mail-type=END,FAIL

cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py YEAR MONTH"
echo $cmd
`$cmd > 'NewMergingYEAR_MONTH.log'`

