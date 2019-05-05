#!/usr/bin/env python
import re,sys,os
import gzip
import argparse
reload(sys)
sys.setdefaultencoding('gb18030')
parser = argparse.ArgumentParser(description='Vcf to MAF converter.')
parser.add_argument('-v', '--vcf', help='the tumor vcf.gz file', required=True)
parser.add_argument('-m', '--method', help='Method for somatic calling: Strelka, muTect, varScan, samtools, unknown, default unknown',choices=['Strelka','muTect','varScan','samtools','unknown','GATK'],default='unknown')
parser.add_argument('-t', '--Tsample', help='Tumor Sample Name', required=True)
parser.add_argument('-n', '--Nsample', help='Normal Sample Name, default None', default='')
parser.add_argument('-s', '--seq_source', help='WGS, WES or other, default: WGS', default='WGS')
parser.add_argument('-p', '--platform', help='Platform for data generation, Hiseq2000, HiseqX, SNParray, ..., default HiseqX', default='HiseqX')
parser.add_argument('-f', '--dbsnp-flag', help='The flag for dbSNP annotation in VCF INFO column, default snp138', default='snp138')
parser.add_argument('-g', '--geneinfo', help='gene_name & Entrez_Gene_Id file, default:/PUBLIC/database/HUMAN/AnnotationDB/Homo_sapiens.gene_info',default='/PUBLIC/database/HUMAN/AnnotationDB/Homo_sapiens.gene_info')
parser.add_argument('-r', '--refseq', help='Refseq bed file, default:/PUBLIC/database/HUMAN/AnnotationDB/annovar_v2/hg19_refGene.txt',default='/PUBLIC/database/HUMAN/AnnotationDB/annovar_v2/hg19_refGene.txt')
parser.add_argument('-o', '--output', help='Output MAF file', required=True)
parser.add_argument('-x', '--infos', help='Info field for append to output', default=None)


args = parser.parse_args()

t2genes = {}
for line in open(args.refseq):
	array = line.strip().split('\t')
	t2genes[array[1]] = array[12]

class VCFline:
	def __init__(self, vcfline):
		self.vcfline = vcfline
		self.list = vcfline.strip().split('\t')
		self.chr = self.list[0]
		self.pos = self.list[1]
		self.id = self.list[2]
		self.ref = self.list[3]
		self.alt = self.list[4]
		self.qual = self.list[5]
		self.filter = self.list[6]
		self.info = self.list[7]
		self.format = self.list[8]
		self.samples = self.list[9:]
		self.infos = self.infoSplit()
		self.genes = self.get_genes()

	def variatClassification(self):
		var_class = \
		{'missense_SNV':'Missense_Mutation',
		 'synonymous_SNV':'Silent',
		 'stopgain_SNV':'Nonsense_Mutation',
		 'stoploss_SNV':'Nonstop_Mutation',
		 'stopgain':'Nonsense_Mutation',
		 'stoploss':'Nonstop_Mutation',
		 'unknown':'RNA',
		 'nonframeshift_deletion':'In_Frame_Del',
		 'frameshift_deletion':'Frame_Shift_Del',
		 'nonframeshift_insertion':'In_Frame_Ins',
		 'frameshift_insertion':'Frame_Shift_Ins',
		 'nonframeshift_substitution':'In_Frame_Ins',
		 'frameshift_substitution':'Frame_Shift_Ins',
		 'frameshift_block_substitution':'Frame_Shift_Ins',
		 'nonframeshift_block_substitution':'Frame_Shift_Ins',
		 'ncRNA_UTR5':'RNA',
		 'ncRNA_UTR3':'RNA',
		 'ncRNA_UTR5,ncRNA_UTR3':'RNA',
		 'ncRNA_exonic,ncRNA_splicing':'Splice_Site',
		 'UTR5':'5\'UTR',
		 'UTR3':'3\'UTR',
		 'UTR5,UTR3':'5\'UTR',
		 'UTR5;UTR3':'5\'UTR',
		 'intronic':'Intron',
		 'ncRNA_intronic':'RNA',
		 'ncRNA_exonic':'RNA',
		 'ncRNA_splicing':'RNA',
		 'exonic,splicing':'Splice_Site',
		 'splicing':'Splice_Site',
		 'exonic;splicing':'Splice_Site',
		 'intergenic':'IGR',
		 'upstream':'5\'Flank',
		 'downstream':'3\'Flank',
		 'upstream,downstream':'5\'Flank',
		 'upstream;downstream':'5\'Flank',
		 '.':'RNA','':'RNA','unknown':'RNA'}
		return var_class

	def FilterFuncs(self):
		myfuncs = ['Missense_Mutation','Nonsense_Mutation','Nonstop_Mutation',\
			   'Splice_Site','In_Frame_Del','Frame_Shift_Del','In_Frame_Ins',\
			   'Frame_Shift_Ins','Frame_Shift_Ins']
		return myfuncs

	def vFunc(self):
		vClass = self.variatClassification()
		if self.infos['Func'].startswith('exonic'):
			return vClass[self.infos['ExonicFunc'].split(';')[0]]
		else:
			return vClass[self.infos['Func'].split(';')[0]]

	def FuncFilter(self, myfuncs):
		if self.vFunc() in myfuncs:
			return True
		else:
			return False
		
	def infoSplit(self):
		dicts = {}
		items = ['Func','Gene','GeneDetail','ExonicFunc','AAChange']
		currentKey = ''
		for each in self.info.split(';'):
			if '=' in each:
				tmp = each.split('=',1)
				if tmp[0] == 'Name' or tmp[0] == 'Score':
					dicts[currentKey] += ';'+each
				else:
					if tmp[0] not in dicts:
						dicts[tmp[0]] = tmp[1]
						currentKey = tmp[0]
				
			else:
				if currentKey in items:
					dicts[currentKey] += ';'+each
				else:
					dicts[each] = 1
		return dicts

	def formatSplit(self, i = 0):
		keys = self.format.split(':')
		values = self.samples[i].split(':')
		return dict(zip(keys,values))

	## info To table
	def toTable(self,infolist,opt='.'):
		return '\t'.join([self.infos.get(each,opt) for each in infolist])

	def simpleVcf(self):
		#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  EC1205_H
		return '%s\t%s\t.\t%s\t%s\t%s\tPASS\t.\tGT\t%s\n' % (self.chr,self.pos,self.ref,self.alt,self.qual,self.formatSplit().get("GT","."))

	def alleleDepth(self, i=0, method='unknown'):
		ref_dp = '0'
		alt_dp = '0'
		formats = self.formatSplit(i)
		if method == 'muTect':
		## GT:AD:BQ:DP:FA:SS       0:79,0:.:79:0.00:0      0/1:64,20:37:84:0.238:2
			ref_dp,alt_dp = formats['AD'].split(',')
		elif method == 'Strelka':
		##SNP DP:FDP:SDP:SUBDP:AU:CU:GU:TU    38:0:0:0:0,0:0,0:37,37:1,1      66:0:0:0:24,24:0,0:42,42:0,0
		##INDEL DP:DP2:TAR:TIR:TOR:DP50:FDP50:SUBDP50   155:155:159,159:0,0:0,0:144.77:0.05:0.00  151:151:115,116:21,21:16,16:137.03:0.14:0.00
			if self.getVT() == 'SNP':
				ref_dp = formats[self.ref+'U'].split(',')[1]
				alt_dp = formats[self.alt+'U'].split(',')[1]
			else:
				alt_dp = formats['TIR'].split(',')[1]
				ref_dp = str(int(formats['DP']) - int(alt_dp))
		elif method == 'samtools':
		## GT:PL:DP:DV:SP  0/1:103,0,255:37:12:8
			alt_dp = formats['DV']
			ref_dp = str(int(formats['DP']) - int(alt_dp))
		elif method == 'varScan':
		## GT:GQ:DP:RD:AD:FREQ:DP4 0/0:.:45:45:0:0%:17,28,0,0      0/1:.:92:73:10:12.05%:29,44,4,6
			if self.getVT() == 'SNP':
				ref_dp = formats['RD']
				alt_dp = formats['AD']
			else:
				dp = int(formats['DP'])
				af = float(self.infos.get('AF1','0'))
				alt_dp = int(dp * af)
				ref_dp  = str(dp - alt_dp)
				alt_dp = str(alt_dp)
		elif method == 'GATK':
			ref_dp,alt_dp = formats['AD'].split(',')[0:2]
		elif method == 'unknown': pass
		return ref_dp,alt_dp

	## variation type: SNP, INDEL
	def getVT(self):
		vType = 'SNP'
		self.alt=self.alt.split(',')[0]
		if len(self.ref) < len(self.alt): 
			vType = "INS"
		elif len(self.ref) > len(self.alt): 
			vType = "DEL"
		else: 
			if  self.ref == '-':
				vType = 'INS'
			elif self.alt == '-':
				vType = 'DEL'
			else:
				vType = "SNP"
		return vType
	## Genotype
	def getGT(self, i = 0):
		formats = self.formatSplit(i)
		gType = formats.get('GT','0/1')
		return gType
	

	def ltFilter(self, name, low):
		if name in self.infos:
			if self.infos[name] == '.':
				return True
			if float(self.infos[name]) < low:
				return True
			else:
				return False
		else:
			return True
		
	def gtFilter(self, name, high):
		if name in self.infos:
			if self.infos[name] == '.':
				return True
			if float(self.infos[name]) >= high:
				return True
			else:
				return False
		else:
			return True

	def StrFilter(self, name, value='.'):
		if name in self.infos:
			if self.infos[name] == value:
				return True
			else:
				return False
		else:
			return True

	def HRunFilter(self, hrun = 5):
		return self.ltFilter('HRun',hrun)

	def DpFilter(self, dp = 3):
		return self.gtFilter('DP',dp)

	def DpFilter2(self, dpT, dp = 3):
		return (dpT >= dp)

	def RepeatFilter(self):
		filter = self.StrFilter('genomicSuperDups')
		return  filter

	## in cosmicDB or with low-pop-freq in 1000G or not in dbSNP	
	def DbFilter(self,dbsnp='snp138',thousand='1000g2012apr_all',cosmic='cosmic68'):
		if (not self.StrFilter(cosmic)) or self.StrFilter(dbsnp):
		#if (not self.StrFilter(cosmic)) or (self.ltFilter(thousand,0.0014) and (not self.StrFilter(thousand))) or self.StrFilter(dbsnp):
			return True
		else:
			return False

	def ScoreFilter(self, dbs=['ljb23_sift','ljb23_pp2hvar','ljb23_pp2hdiv','ljb23_mt']):
		## D:Deleterious;Probably damaging;disease_causing A:disease_causing_automatic
		## P:possibly damaging B:benign T:tolerated P:polymorphism_automatic
		scores1 = {'D':1, 'T':0, 'B':0, 'P':0.5, '.':0}
		scores2 = {'A':1, 'D':1, 'N':0, 'P':0, '.':0} ## ljb23_mt
		myscore = 0
		for each in dbs:
			s = self.infos.get(each,'N').split(',')[-1]
			if each == 'ljb23_mt':
				myscore += scores2[s]
			else:
				myscore += scores1[s]
		if myscore >= 1:
			return True
		else:
			return False

	def get_genes(self):
		#gname = self.infos.get('GeneName',self.infos.get('Gene','-'))
		gname = self.infos.get('GeneName',self.infos.get('Genename',self.infos.get('Gene','-')))
		gnames = [each.split(';') for each in gname.replace('Name=','').split(',')]
		genes = []
		for each in gnames:
			genes += each
		return genes[0]

	def get_transcripts(self):
		tname = self.infos.get('Gene','-')
		tnames = [each.split(';') for each in tname.replace('Name=','').split(',')]
		transcripts = []
		for each in tnames:
			transcripts += each
		return transcripts

	def get_one_gene(self):
		genes = [t2genes.get(each,'.') for each in self.get_transcripts()]
		aachanges = self.get_aachange().split(':')
		if aachanges[0] in genes:
			return aachanges[0]
		else:
			return genes[0]

	def get_aachange(self):
		aachange = self.infos.get('AAChange','').split(',')[0]
		if self.vFunc() == 'Splice_Site' or 'UTR' in self.vFunc():
			aachange = self.infos.get('GeneDetail','').split(';')[0]
		return aachange


def safe_open(file_name,mode='r'):
	try:
		if not file_name.endswith('.gz'):
			return open(file_name,mode)
		else:
			import gzip
			return gzip.open(file_name,mode)
	except IOError:
		print file_name + ' do not exist!'

tvcf = args.vcf
source = args.seq_source
sampleN = args.Nsample
sampleT = args.Tsample
platform = args.platform
method = args.method

add_infos = []
if args.infos:
	add_infos = args.infos.split(',')

nameMapping = {'primary':{},'secondary':{}}
description = {}
for line in safe_open(args.geneinfo,'r'):
	if line.startswith('#'):
		continue
	array = line.strip().split('\t')
	nameMapping['primary'][array[2]] = {'eid':array[1],'gid':array[2],'type':array[9]}
	if not array[4] == '-':
		for each in array[4].split('|'):
			nameMapping['secondary'][each] = {'eid':array[1],'gid':array[2],'type':array[9]}
	description[array[2]] = array[8]

def get_gene(id,type='gid'):
	return nameMapping['primary'].get(id,nameMapping['secondary'].get(id,{'eid':'','gid':id, 'type':'unknown'}))[type]

def format_gene2(genes):
	list1 = []
	list2 = []
	for each in genes:
		if '-' in each:
			list2.append(each)
		else:
			list1.append(each)
	genes = list1 + list2
	myGenes = [(get_gene(each,'gid'),get_gene(each,'eid')) for each in genes if get_gene(each,'type')=='protein-coding'] + \
			[(get_gene(each,'gid'),get_gene(each,'eid')) for each in genes if get_gene(each,'type')!='protein-coding']
	return myGenes[0]
def format_gene1(AA):
	genes=AA.split(':')[0]
	genes=[genes]
	myGenes = [(get_gene(each,'gid'),get_gene(each,'eid')) for each in genes if get_gene(each,'type')=='protein-coding'] + \
		  [(get_gene(each,'gid'),get_gene(each,'eid')) for each in genes if get_gene(each,'type')!='protein-coding']
	return myGenes[0]

title = ['Hugo_Symbol','Entrez_Gene_Id','Center','NCBI_Build','Chromosome','Start_position','End_Position','Strand','Variant_Classification',
	 'Variant_Type','Reference_Allele','Tumor_Seq_Allele1','Tumor_Seq_Allele2','dbSNP_RS','dbSNP_Val_Status','Tumor_Sample_Barcode',
	 'Matched_Norm_Sample_Barcode','Match_Norm_Seq_Allele1','Match_Norm_Seq_Allele2','Tumor_Validation_Allele1','Tumor_Validation_Allele2',
	 'Match_Norm_Validation_Allele1','Match_Norm_Validation_Allele2','Verification_Status','Validation_Status','Mutation_Status','Sequencing_Phase',
	 'Sequence_Source','Validation_Method','Sequencer','Tumor_Sample_UUID','Matched_Norm_Sample_UUID','t_ref_count','t_alt_count','n_ref_count',
	 'n_alt_count','t_AF','AAchange','COSMIC','SuperDups','Description']+add_infos


maf = safe_open(args.output,'w')
maf.write('\t'.join(title)+'\n')

for line in safe_open(tvcf,'r'):
	if line.startswith('#'):
		continue
	line = line.replace("\\x3e","=")
	line = line.replace("\\x3b",";")
	vcfline = VCFline(line)
	aachange = vcfline.get_aachange()
	gid,eid = format_gene1(aachange)
	if vcfline.vFunc() in ['3\'UTR','5\'UTR','Splice_Site']:
		gid,eid = format_gene2([vcfline.get_genes()])
	if vcfline.vFunc() in ['IGR', '5\'Flank', '3\'Flank']:
		gid = '.'
		eid = ''
	# Filter
	## software Filter
	if not (vcfline.filter == '.' or vcfline.filter == 'PASS'):
		continue
	#############################################################################
	##                    allele depth                                    #######
	#############################################################################
	ref_dpT = alt_dpT = ref_dpN = alt_dpN = '0'
	gt = vcfline.getGT()
	if len(vcfline.samples) == 1:
		ref_dpT,alt_dpT = vcfline.alleleDepth(0,args.method)
	else:
		ref_dpN,alt_dpN = vcfline.alleleDepth(0,args.method)
		ref_dpT,alt_dpT = vcfline.alleleDepth(1,args.method)
		if args.method == 'muTect' and '/' in vcfline.formatSplit()['GT']:
			ref_dpN,alt_dpN,ref_dpT,alt_dpT = ref_dpT,alt_dpT,ref_dpN,alt_dpN
			gt = vcfline.getGT(1)
	alt_dpT2 = alt_dpT
	if ',' in alt_dpT:
		alt_dpT2 = sum([int(e) for e in alt_dpT.split(',')])
	alt_dpT2 = int(alt_dpT2)
	## allele type
	alle1 = vcfline.ref
	alle2 = vcfline.alt
	if gt == '0/1':
		alle1 = vcfline.ref

	## allele Frequency
	if int(alt_dpT2)+int(ref_dpT) == 0:
		af_T = '0'
	else:
		af_T = '%0.3f'%(float(alt_dpT2)/(int(alt_dpT2)+int(ref_dpT)))
	#############################################################################
	## mafline
	mafline = [gid, eid, 'Novogene', 'GRCh37', vcfline.chr, vcfline.pos, vcfline.pos, '+', \
		vcfline.vFunc(), vcfline.getVT(), vcfline.ref, alle1, alle2, vcfline.infos.get(args.dbsnp_flag,''), \
		'', sampleT, sampleN, '', '', '', '', '', '', '', 'Untested', 'Somatic', '', source, 'none', platform, \
		sampleT, sampleN, ref_dpT, alt_dpT, ref_dpN, alt_dpN, af_T, aachange,vcfline.infos.get('cosmic68','').replace('ID=',''), \
		vcfline.infos.get('genomicSuperDups','.'), description.get(gid,'.')] + [vcfline.infos.get(each,'.') for each in add_infos]

	maf.write('\t'.join(mafline)+'\n')
maf.close()

