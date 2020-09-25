#!/bin/bash
#SBATCH --job-name="JNAME" 
#SBATCH -t 10:00:00 
#SBATCH -p coaps_q 
#SBATCH -n 2
#SBATCH -N 1 
#SBATCH --mem=64G 
#SBATCH --mail-type=END,FAIL 
 
module load intel-openmpi      
module load anaconda3.7.3      

start_date_str="START"
end_date_str="FINISH"
inc_per_run=INC

run_name="RUNNAME"
cmd="srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 1_MergeRuns.py ${start_date_str}:0 ${end_date_str}:0 False ${run_name} ${inc_per_run}"
echo $cmd
`$cmd > "Merge_JNAME.log"`
