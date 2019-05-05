#!usr/bin/env python
#coding=utf-8
import re
import sys
f=open('uniprot_sprot.fasta','r')
out=open('uniprot_sprot_select.fasta','w')
r1=re.compile(r'OS=(.*) GN=')
r2=re.compile(r'OS=(.*)')
content=''
h=f.readline()
line=f.readline()
while line.strip():
    if line.strip().startswith('>'):
       s=r1.findall(h)
       if s==[]:
           s=r2.findall(h)
       if s!=[]:
           if s[0]=='Homo sapiens' or s[0]=='Mus musculus':
               out.write(h+content)
       else:
           print 'Error',h
           sys.exit()
       h=line
       content=''
    else:
       content+=line
    line=f.readline()

s=r1.findall(h)
if s==[]:
    s=r2.findall(h)
if s!=[]:
    if s[0]=='Homo sapiens' or s[0]=='Mus musculus':
        out.write(h+content)
else:
    print 'Error',h
    sys.exit()
