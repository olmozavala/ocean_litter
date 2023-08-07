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

module load intel-openmpi
module load anaconda3.7.3

cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py ${c_start_date}:0 ${c_end_date}:0 True True False ${run_name}_${c_start_date}_${c_end_date}"
`$cmd > 'CurrentRun20YEAR_MONTH.log'`

