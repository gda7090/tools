#!/usr/bin/env python
#coding=utf-8
import sys
import os
import argparse
parser =argparse.ArgumentParser(description="zcat data,zcat nova下机数据，lane1 和 lane2")
parser.add_argument('--zcat_list',help="第一列为下机路径1，第二列为下机路径2 第三列为文库名 第四列为样本名称的文件",required=True)
parser.add_argument('--type',help="pe or se",required=True)
argv = vars(parser.parse_args())
zcat_list=argv['zcat_list'].strip()
type=argv['type'].strip()
f=open(zcat_list,'r').readlines()
if type=='se':
    for eachline in f:
        each=eachline.strip().split("\t")
        path_1=each[0].strip()
        path_2=each[1].strip()
        library=each[2].strip()
        sample=each[3].strip()
        os.system('rm %s*.gz'%(sample))
        f=open('zcat_'+sample+'.sh','w')
        f.write("zcat %s/%s/%s_L1_1.fq.gz %s/%s/%s_L2_1.fq.gz | gzip > %s.fq.gz\n" %(path_1,library,library,path_2,library,library,sample))
        f.write("zcat %s/%s/%s_L1_1.adapter.list.gz %s/%s/%s_L2_1.adapter.list.gz | gzip > %s.adapter.list.gz\n" %(path_1,library,library,path_2,library,library,sample))
        f.close()
        os.system('qsub -V -cwd -l vf=2g -S /bin/bash zcat_%s.sh'%(sample))
elif type=='pe':
    for eachline in f:
        each=eachline.strip().split("\t")
        path_1=each[0].strip()
        path_2=each[1].strip()
        library=each[2].strip()
        sample=each[3].strip()
        os.system('rm %s*.gz'%(sample))
        f=open('zcat_'+sample+'.sh','w')
        f.write("zcat %s/%s/%s_L1_1.fq.gz %s/%s/%s_L2_1.fq.gz | gzip > %s_1.fq.gz\n" %(path_1,library,library,path_2,library,library,sample))
        f.write("zcat %s/%s/%s_L1_1.adapter.list.gz %s/%s/%s_L2_1.adapter.list.gz | gzip > %s_1.adapter.list.gz\n" %(path_1,library,library,path_2,library,library,sample))
        f.write("zcat %s/%s/%s_L1_2.fq.gz %s/%s/%s_L2_2.fq.gz | gzip > %s_2.fq.gz\n" %(path_1,library,library,path_2,library,library,sample))
        f.write("zcat %s/%s/%s_L1_2.adapter.list.gz %s/%s/%s_L2_2.adapter.list.gz | gzip > %s_2.adapter.list.gz\n" %(path_1,library,library,path_2,library,library,sample))
        f.close()
        os.system('qsub -V -cwd -l vf=2g -S /bin/bash zcat_%s.sh'%(sample))
