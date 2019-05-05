#!/usr/bin/python
import os,sys,HTSeq

bam=HTSeq.BAM_Reader(sys.argv[1])

for each in bam:
	if each.aligned and each.mate_aligned:
		if each.pe_which == 'first':
			print abs(each.inferred_insert_size)

