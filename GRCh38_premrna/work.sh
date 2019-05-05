awk 'BEGIN{FS="\t"; OFS="\t"} $3 == "transcript"{ $3="exon"; print}' \
/NJPROJ2/RNA/database/10X_reference/GRCh38/genes/genes.gtf >GRCh38.premrna.gtf
/NJPROJ2/RNA_S/software/cellranger-2.2.0/cellranger mkref --genome=GRCh38_premrna \
                   --fasta=/NJPROJ2/RNA/database/10X_reference/GRCh38/fasta/genome.fa \
                   --genes=GRCh38.premrna.gtf


