#!/bin/bash
end_date_str="2020-01-01"
inc_per_run=30

# Iterate years
for j in {1..20..1}
#for j in {20..20..1}
do
    cur_year=$(printf "%02d" $j)
    # Iterate Months
    for i in {1..12..1}
    do
        cur_month=$(printf "%02d" $i)
        start_date_str="20${cur_year}-${cur_month}-01"
        run_name="TenYears_YesWinds_YesDiffusion_NoUnbeaching_20${cur_year}_${cur_month}"
        jname="${cur_year}_${cur_month}"
        sed --expression="s/START/${start_date_str}/g" --expression="s/JNAME/m_${jname}/g" --expression="s/FINISH/${end_date_str}/g" --expression="s/INC/${inc_per_run}/g" --expression="s/RUNNAME/${run_name}/" general_merge.sh > merge_20${cur_year}_${cur_month}.sh 
        sbatch merge_20${cur_year}_${cur_month}.sh
    done
done
