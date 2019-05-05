#!/usr/bin/env python
#_*_coding:utf-8_*_


import os,pwd
import re
import glob
import sys
import argparse
#from argparse import RawTexHelpFormatter
parser=argparse.ArgumentParser(description="Extract informations")#, formatter_class=RawTextHelpFormatter)
parser.add_argument('--pwd',help="Path of Project Directory for analysis")
parser.add_argument('--qclist_info',help="The file of sample's information",required=True)
parser.add_argument('--pn',help="The Proj_Name",required=True)
parser.add_argument('--odir',help="the path of output file",required=True)
#parser.add_argument('--info_name',help="The person who analyzes the information (Required)\n",required=True)

argv=vars(parser.parse_args())
projdir=argv['pwd'].strip()
sample_info=argv['qclist_info'].strip()
pn_txt=argv['pn'].strip()
odir=argv['odir'].strip()
#info_name=argv['info_name'].strip()

stat = os.stat(projdir)
uid = stat.st_uid
getuid=pwd.getpwuid(uid)[0]

dirname = os.path.split(projdir)[1]
projname = dirname+'.sample_list.stat'
#print projname
#seqmethod,connum,disname,date=dirname.split('.',3)
date=dirname.split('.')[-1]

odirdate=odir+'/'+date

datedirname=odirdate+'/'+projname

if not os.path.exists(odirdate):

	os.system('mkdir -m 777 %s' %odirdate)
	if not os.path.exists(odirdate+'/'+projname):
                file=open(odirdate+'/'+projname,'w')
                file.write('\t'.join(['PatientID','SampleID','LibID','Path','type','contract_number','project_title','project_number','Author','infopath','\n']))
        else:
                file=open(odirdate+'/'+projname,'a')
		
else:
	if not os.path.exists(odirdate+'/'+projname):
		file=open(odirdate+'/'+projname,'w')
		file.write('\t'.join(['PatientID','SampleID','LibID','Path','type','contract_number','project_title','project_number','Author','infopath','\n']))
	else:
		file=open(odirdate+'/'+projname,'a')

line=open(sample_info,'r')

with open(pn_txt,'r') as pn:
        pnlist=pn.readlines()[0].strip("\n")
for lines in line :
	a=lines.strip().split('\t')
	a.pop(0)
	a.pop(3)
	a.pop(5)
	file.write('\t'.join(a)+'\t'+pnlist+'\t'+getuid+'\t'+projdir+'\n')
file.close()
b=odirdate+'/'+projname
os.system('head -1 %s > header.txt' %b)
os.system('sed 1d %s > tmp.txt' %b)
os.system('sort -u tmp.txt >> header.txt')
os.system('rm -f tmp.txt %s' %datedirname) 
os.system('mv header.txt %s' %datedirname) 
