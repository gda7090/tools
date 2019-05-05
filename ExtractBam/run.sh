cd $1 ##extract bam path
python /NJPROJ2/CANCER/share/Module/AfterSale/ExtractBam/code/get_files.py $2 $3 &&\
python /NJPROJ2/CANCER/share/Module/AfterSale/ExtractBam/code/bam2html.py \
    -f dot \
    -g gene_list \
    -b bam_list \
    -x 5 \
    -k 150 \
    -o $1 \
    -p gene_info \
    -r b37
