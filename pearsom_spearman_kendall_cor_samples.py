#coding=utf-8
import sys
from scipy.stats import pearsonr,spearmanr,kendalltau
import numpy as np
import math,itertools
from collections import defaultdict


dict1=defaultdict(list)

for eachline in open('merged.tpm','r'):
    lst1=eachline.strip().split('\t')
    if eachline.startswith('circ'):
        lst_sample=lst1[1:]
    else:
        for each_key in lst_sample: 
            dict1[each_key].append(lst1[lst_sample.index(each_key)+1])

for each_couple in itertools.combinations(lst_sample,2):
    lst_2d=[]
    x=[]
    y=[]
    flager=0
    for each_sample in each_couple:
        flager+=1
        if flager%2!=0:
            a=dict1[each_sample]
        else:
            b=dict1[each_sample]
    lst_2d=zip(a,b)
    for each_x,each_y in lst_2d:
        x.append(math.log10(float(each_x)+1))
        y.append(math.log10(float(each_y)+1))
    m=np.mat(lst_2d)
    #y=np.mat(lst_2d).astype(float).any()
    y=tuple(y)
    x=tuple(x)
    aa,a=pearsonr(x,y)
    aa2=math.pow(aa,2)
    bb,b=spearmanr(m)
    #bb,b=spearmanr(x,y)
    cc,c=kendalltau(x,y)
    print '%s pearson r,p,r2分别是:' % (','.join(list(each_couple)))
    print aa,a,aa2
    print '%s spearman r,p分别是:' % (','.join(list(each_couple)))
    print bb,b
    print '%s kendall  r,p分别是:' % (','.join(list(each_couple)))
    print cc,c
