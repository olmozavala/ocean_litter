#!/bin/bash

#SBATCH --job-name="OP 2010"
#SBATCH --mail-type="ALL"
#SBATCH -t  100:00:00
#SBATCH -p coaps18_q
#SBATCH -N 2
#SBATCH --mem=64G

module load intel-openmpi
module load anaconda3.7.3
#conda activate py3_parcels_mpi
#source /gpfs/home/osz09/.bashrc
#source activate py3_parcels_mpi

# Single year starting Jan 1st
#mpirun -np 10 /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_WorldLitter.py '2010-01-01:0' '2011-01-01:0'
# Five years single release staring Jan 1st
mpirun -np 10 /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 0_WorldLitter.py '2010-01-01:0' '2014-12-31:0'
# Five years single release staring Jul 1st
#mpirun -np 10 /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_WorldLitter.py '2010-07-01:0' '2015-12-31:0'
# Five years single release staring Jan 1st 2011
#mpirun -np 10 /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_WorldLitter.py '2011-01-01:0' '2015-12-31:0'
# Five years single release staring Jul 1st 2011
#mpirun -np 10 /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_WorldLitter.py '2011-07-01:0' '2015-12-31:0'

