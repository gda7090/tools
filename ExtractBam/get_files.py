
# coding: utf-8

"""
This is a google style docs.
 Author: SongZhirui
 
 E-mail: songzhiruifly@hotmail.com
 
 Parameters:
   param1 - path: absolute path of bam file, like some Projdir/Mapping/
   param2 - file: a file format like maf
   param3 - str: 
      
 Returns:
   outfile : 
       gene_info ; gene_list; bam_list
 
 Raises:
   error: if any errors happend, you need to rerun the script and the bug only
          raised with too many samples.

 Example:
   eg: python get_files.py Projdir/Mapping/ pos.txt
"""
import sys
import os
#/PROJ/HUMAN/Cancer/WES.C101SC16120632.lungcancer60li.20170801/Mapping
path = sys.argv[1]
header = 'Sample_ID\tChromosome\tStart_Position\tHugo_Symbol\n'

out1 = open('gene_list', 'w')
out2 = open('gene_info', 'w')
out2.write(header)
os.system('rm -rf bam_list')
with open(sys.argv[2]) as inf:
	for line in inf:
		if not line.startswith('Hugo_Symbol'):
			alist = line.rstrip('\n').split('\t')
			if len(alist) > 4:
				id,chr,pos,gene = alist[15],alist[4], alist[5], alist[0]
			else:
				id,chr,pos,gene = alist
			line_info = '\t'.join([id, chr, pos, gene]) + '\n'
			line_list = '\t'.join([chr, pos, gene]) + '\n'
			bampath = os.path.join(path, id, id + '.final.bam')
			if os.path.exists(bampath):
				os.system('echo %s >> bam_list'%bampath)
			else:
				print '%s not exists!!!'%bampath
				sys.exit(1)
			out1.write(line_list)
			out2.write(line_info)

out1.close()
out2.close()
print('\n'.join([''.join([('Love'[(x-y) % len('Love')] 
      if ((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3 <= 0 else ' ') 
      for x in range(-30, 30)]) for y in range(30, -30, -1)]))
