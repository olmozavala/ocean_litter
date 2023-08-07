#!/bin/bash

sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" generalrun_hpc.sh > run20${cur_year}_${cur_month}.sh
sbatch run20${cur_year}_${cur_month}.sh

for j in {21..21..1}
do
    cur_year=$(printf "%02d" $j)
    # Iterate Months
    for i in {1..12..1}
    do
        cur_month=$(printf "%02d" $i)
        echo 'Finishing year for Year: 20'${cur_year} 'Month:'${cur_month}
        # ----------- For HPC ------------
        sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" general_merge.sh > runMerge20${cur_year}_${cur_month}.sh
        sbatch runMerge20${cur_year}_${cur_month}.sh
    done
done


echo 'Finishing year for Year: 20'${cur_year} 'Month:'${cur_month}
# ----------- For HPC ------------
sed --expression="s/MONTH/${cur_month}/g" --expression="s/YEAR/${cur_year}/g" general_merge.sh > runMerge20${cur_year}_${cur_month}.sh
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2017 5`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2010 2`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2010 3`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2010 5`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2010 7`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2010 9`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2010 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2011 3`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2011 5`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2012 5`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2012 7`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2012 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2013 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2013 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2013 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2014 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2014 1`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2015 2`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2015 4`
`srun /gpfs/home/osz09/.conda/envs/py3_parcels_mpi/bin/python 7_Merge_Merged_Adding_New_Years.py 2017 5`
