#!/bin/bash

#for i in {1..12..1}
for i in {10..12..1}
do
    cur_month=$(printf "%02d" $i)
    echo ${cur_month}
    sed -e "s/MONTH/${cur_month}/g" config/MainConfigExample.py > config/MainConfig.py
    python 4_MakeHistogram.py
done
