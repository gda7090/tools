#!usr/bin/env python
#coding=utf-8



import re
import argparse

parser=argparse.ArgumentParser(description='从fasta文件去掉seqname后面的多余信息，只留下>chr1')
parser.add_argument('-fa_prim',required=True,help='输入fasta文件')
parser.add_argument('-fa_mature',required=True,help='输出fasta文件')
argv=parser.parse_args()

out=open(argv.fa_mature,'w')

seq_name=''
seq=''
for line in open(argv.fa_prim,'r'):
    if line.startswith('>'):
        seq_name=line.strip().split(' ')[0]
        out.write(seq_name+'\n')
    else:
        out.write(line)

