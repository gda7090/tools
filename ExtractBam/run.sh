cd $1 ##extract bam path
python ExtractBam/code/get_files.py $2 $3 &&\
python ExtractBam/code/bam2html.py \
    -f dot \
    -g gene_list \
    -b bam_list \
    -x 5 \
    -k 150 \
    -o $1 \
    -p gene_info \
    -r b37
