#!/usr/bin/python
#coding=utf-8
import os,pwd
import re
import glob
import sys
import shlex
import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(description="Extract informations", formatter_class=RawTextHelpFormatter)
parser.add_argument('--pwd',help="Path of Project Directory for analysis (Required)",required=True)
parser.add_argument('--project',help="The file of project information(Required)\n"
                                        "The file has 2 tab delimited fields:\n"
                                        "projectID  project_name",required=True)
parser.add_argument('--odir',help="the path of output files (Required)",required=True)

argv=vars(parser.parse_args())
projdir=argv['pwd'].strip()
pn_txt=argv['project'].strip()
odir = argv['odir'].strip()

## extract proj name and proj number
D=open(pn_txt,'r')
for x in D.readlines():
    y=x.strip().split()
    Proj_name=y[1]
    Proj_number=y[0]
    
stat = os.stat(projdir)
uid = stat.st_uid
getuid=pwd.getpwuid(uid)[0]
dirname = os.path.split(projdir)[1]

qc_stat=open(projdir+"/QC/QC_data_mapping.stat",'r')
lines=qc_stat.readlines()
QClines=lines[0:]

sam_info={}
for n in QClines:
    i=n.strip().split()
    sam_info[i[1]]=i[7]

if not os.path.exists(odir+'/scRNA_project.info.xls'):
    allinfo=open(odir+'/scRNA_project.info.xls','w')
    tmp=['Proj_number','Proj_name','SampleID','Clean_data','Estimated Number of Cells','Mean Reads per Cell','Median Genes per Cell','Number of Reads','Valid Barcodes','Sequencing Saturation','Q30 Bases in Barcode','Q30 Bases in RNA Read','Q30 Bases in UMI','Reads Mapped to Genome','Reads Mapped Confidently to Genome','Reads Mapped Confidently to Intergenic Regions','Reads Mapped Confidently to Intronic Regions','Reads Mapped Confidently to Exonic Regions','Reads Mapped Confidently to Transcriptome','Reads Mapped Antisense to Gene','Fraction Reads in Cells','Total Genes Detected','Median UMI Counts per Cell']
    head ='\t'.join(tmp)+"\n"
    allinfo.write(head)
else:
    allinfo=open(odir+'/scRNA_project.info.xls','a')

for k,m in sam_info.items():
#    print(k,m)
    cellranger_metrics=os.path.join(projdir,'CellRanger/'+k+'/'+k+'/outs/metrics_summary.csv')
    celline = open(cellranger_metrics).readlines()[1].strip()
    celline = celline.replace("%","\%")
    celline = celline.replace(".","\.")
    str=shlex.shlex(celline,posix=True)
    str.whitespace=','
    str.whitesapce_split=True
    tmpline=list(str)
    tmp=[Proj_number,Proj_name,k,sam_info[k]]
    tmp.extend(tmpline)
    tmp ='\t'.join(tmp) + "\n"
    allinfo.write(tmp)    
