#!/user/bin/python 
#coding=utf8

import os
import argparse
import ConfigParser

parse=argparse.ArgumentParser(description='10X analysis pipeline')
parse.add_argument('--species',help='the name of species ')
parse.add_argument('--dir',help='dir of project')
parse.add_argument('--transcriptome',help='the name of transcriptome')

argv=parse.parse_args()
species=argv.species.strip()
dir=argv.dir.strip(' ')
transcriptome=argv.transcriptome

mapfile=open(dir+'/config/mapfile')
samplelist=[]
for eachline in mapfile:
        eachline=eachline.strip().split('\t')
        samplelist.append(eachline[-1])
samplelist2=list(set(samplelist))

for eachS in samplelist2:
	#os.system('mkdir -p %s/QC/%s/cleandata' %(dir,eachS))
	os.system('mkdir -p %s/CellRanger/%s' %(dir,eachS))

	if species=="GRCh38" and transcriptome == None:
		transcriptome='GRCh38_premrna/GRCh38_premrna'
		annotation='database/genome/GRCh38/GRCh38_gene.txt'
	if species=="mm10" and transcriptome == None:
		transcriptome='database/10X_reference/refdata-cellranger-mm10-1.2.0'
		annotation='database/genome/GRCm38/GRCm38_gene.txt'
	if species=="Dr" and transcriptome == None:
		transcriptome="database/10X_reference/Danio_rerio/Danio_rerio"
		
	#ln -s cleandata + cellranger
	cellranger=open(dir+'/CellRanger/'+eachS+'/'+eachS+'_cell.sh','w+')
#	cellranger.write('ln -s %s/QC/%s/%s_S1_L001_R1_001.fastq.gz  %s/QC/%s/cleandata/\n' %(dir,eachS,eachS,dir,eachS))
#	cellranger.write('ln -s %s/QC/%s/%s_S1_L001_R2_001.fastq.gz %s/QC/%s/cleandata/\n\n' %(dir,eachS,eachS,dir,eachS))
	cellranger.write('cellranger-2.2.0/cellranger  count --id=%s \\\n' %(eachS))
	cellranger.write('			--transcriptome=%s \\\n' %(transcriptome))
	cellranger.write('			--fastqs=%s/QC/%s/clean \\\n' %(dir,eachS))
	cellranger.write('			--sample=%s \\\n\n' %(eachS))
	cellranger.write('software/cellranger-2.2.0/cellranger  mat2csv %s/CellRanger/%s/%s/outs/filtered_gene_bc_matrices  %s/CellRanger/%s/%s/outs/%s_gene_bar.csv_temp\n' %(dir,eachS,eachS,dir,eachS,eachS,eachS))	
	cellranger.write('perl pipeline/Advanced/add_name/cbind_rpkm_genename.pl %s/CellRanger/%s/%s/outs/%s_gene_bar.csv_temp %s %s/CellRanger/%s/%s/outs/%s_gene_bar.csv\n' %(dir,eachS,eachS,eachS,annotation,dir,eachS,eachS,eachS))
	cellranger.write('rm %s/CellRanger/%s/%s/outs/%s_gene_bar.csv_temp\n' %(dir,eachS,eachS,eachS))

