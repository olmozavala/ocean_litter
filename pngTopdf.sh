cd .
FILES=$(ls *png)
mkdir temp
cd temp
for file in $FILES; do BASE=$(echo $file | sed 's/.png//g'); convert ../$BASE.png $BASE.pdf; done &&
gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=../ReachedTablesData.pdf *.pdf
cd ..
rm -r temp
