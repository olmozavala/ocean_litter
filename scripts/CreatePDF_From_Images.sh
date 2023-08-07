#!/bin/bash

cd ../table_images
#montage -mode concatenate -limit memory 2024MiB -tile 2x2 *.png -resize 840x690 ../scripts/Tables.pdf
montage -mode concatenate -tile 2x2 *.png  ../data/World_Litter_Countries_Stats/ReachedTablesData.pdf
echo "Done! file saved at ../data/World_Litter_Countries_Stats/ReachedTablesData.pdf"
cd ../scripts

