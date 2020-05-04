#!/bin/bash

#SBATCH --job-name="OP 2010"
#SBATCH -t  300:00:00
#SBATCH -p coaps_q
#SBATCH -n 32
#SBATCH --mem=64G
#SBATCH --mail-type=FAIL

module load intel-openmpi
module load anaconda3.7.3

srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py '2010-01-01:0' '2010-01-05:0' 'True' 'True' 'True' 'OneYear_Currents_Winds_Diffusion' > OneYear_Currents_Winds_Diffusion.log

