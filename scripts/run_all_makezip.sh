#!/bin/bash

for i in {1..12..1}
do
    cur_month=$(printf "%02d" $i)
    echo ${cur_month}
    sed -e "s/MONTH/${cur_month}/g" config/MainConfigExample.py > config/MainConfig.py
#    sed -e "s/MONTH/${cur_month}/g" config/MainConfigExampleCOAPS.py > config/MainConfig.py
    python 2_OceanParcels_to_JSON_and_ZIP_V2.py
done
