import argparse
import glob
import os
import re
parser = argparse.ArgumentParser(description="cluster enrichment analysis")
parser.add_argument('--indir',help='the directory of output of cellranger',metavar='')
parser.add_argument('--sampleid',help='the name of cellranger id ',metavar='')
parser.add_argument('--pipeline',help='the directory of pipline',metavar='')
parser.add_argument("--species", help="the species number",required=True)
parser.add_argument('--UMI',help='the UMI value used to be select sepecial marker',default=1)
parser.add_argument('--qvalue',help='the  qvalue used to be select sepecial marker',default=0.05)
parser.add_argument("--outdir", help="the output directory",required=True)


argv=vars(parser.parse_args())

species=argv['species']
indir=argv['indir']
sample=argv['sampleid']
outdir=argv['outdir']
pipeline=argv['pipeline']
UMI=float(argv['UMI'])
qvalue=float(argv['qvalue'])

if pipeline == None:
        pipeline='/NJPROJ2/RNA_S/pipeline/10X_pipeline/pipeline1.1'
if pipeline != None:
        pipeline=pipeline.strip()


keggid=pipeline+'/config/keggid.txt'
abbr=''
if species=='mm10':
	abbr='mmu'
	go='/NJPROJ1/RNA/database/genome/Animal/Mus_musculus/Mus_musculus_Ensemble_90/Mus_musculus_Ensemble_90_go.txt'
	kegg='/NJPROJ1/RNA/database/genome/Animal/Mus_musculus/Mus_musculus_Ensemble_90/Mus_musculus_Ensemble_90_mmu_kegg.txt'
	keggdir='/NJPROJ1/RNA/database/kegg/'+abbr
	tf='/NJPROJ1/RNA/database/genome/Animal/Mus_musculus/Mus_musculus_Ensemble_90/Mus_musculus_Ensemble_90_tf.txt'
	ppi='/NJPROJ1/RNA/database/genome/Animal/Mus_musculus/Mus_musculus_Ensemble_90/Mus_musculus_Ensemble_90_10090_ppi.txt'
	taxon='10090'

if species=='GRCh38':
	abbr='hsa'
	go='/NJPROJ1/RNA/database/genome/Animal/Homo_sapiens/Homo_sapiens_Ensemble_90/Homo_sapiens_Ensemble_90_go.txt'
	kegg='/NJPROJ1/RNA/database/genome/Animal/Homo_sapiens/Homo_sapiens_Ensemble_90/Homo_sapiens_Ensemble_90_hsa_kegg.txt'
	keggdir='/NJPROJ1/RNA/database/kegg/'+abbr
	tf='/NJPROJ1/RNA/database/genome/Animal/Homo_sapiens/Homo_sapiens_Ensemble_90/Homo_sapiens_Ensemble_90_tf.txt'
	ppi='/NJPROJ1/RNA/database/genome/Animal/Homo_sapiens/Homo_sapiens_Ensemble_90/Homo_sapiens_Ensemble_90_9606_ppi.txt'
	taxon='9606'


txt=glob.glob('%s/%s/outs/analysis/diffexp/*/differential_expression.csv' %(indir,sample))

cluster_list=[]
for each in txt:
	eachcluster=each.strip().split('/')[-2]
	cluster_list.append(eachcluster)

cluster_list2=list(set(cluster_list))

if not os.path.exists(outdir):
		os.system('mkdir %s' % (outdir))
os.system('mkdir -p %s' % (outdir+'/Cluster/'+sample))
os.system('mkdir -p %s' % (outdir+'/GO/'+sample))
os.system('mkdir -p %s' % (outdir+'/KEGG/'+sample))
os.system('mkdir -p %s' % (outdir+'/TF/'+sample))
os.system('mkdir -p %s' % (outdir+'/Reactome/'+sample))
os.system('mkdir -p %s' % (outdir+'/PPI/'+sample))

root_dir=os.getcwd()
Step1Sh=open(root_dir+'/'+sample+'_enrich_step2.sh','w')
for eachC in cluster_list2:
	os.system('mkdir  %s/Cluster/%s/%s' %(outdir,sample,eachC))
	os.chdir('%s/Cluster/%s/%s' %(outdir,sample,eachC))
	f1=open('%s/%s/outs/analysis/diffexp/%s/differential_expression.csv' %(indir,sample,eachC),'r')
	title=f1.readline().strip(' ').split(',')
	list=[]
	for each  in title:
        	if each.startswith('Cluster'):
                	m = re.match('Cluster[\s](\d+)',each)
	                if m.group(0) not in list:
        	                list.append(m.group(0))
	n=0
	for i,eachcluster in enumerate(list):
	        f_out=open(eachcluster.replace(' ','_')+'.xls','w')
        	f_out.write('Gene ID\tGene Name\t'+eachcluster+' Mean UMI Counts\t'+eachcluster+' Log2 fold change\t'+eachcluster+' Adjusted p value\n')
		f1.seek(0)
        	f1.readline()
        	for  eachline in f1:
                	line=eachline.strip().split(',')
	                if float(line[n+2]) > UMI and float(line[n+3]) > 0  and  float(line[n+4]) < qvalue:
        	                f_out.write(line[0]+'\t'+line[1]+'\t'+'\t'.join(line[n+2:n+5])+'\n')
    	        n+=3
	        f_out.close()

	cluster_txt =glob.glob('%s/Cluster/%s/%s/Cluster_*.xls' %(outdir,sample,eachC))
	list=[]
	for each2 in cluster_txt: 
		ID=each2.strip().split('/')[-1].split('.')[0]
		list.append(ID)
	for eachID in list:
            	Step1Sh.write('mkdir -p  %s/GO/%s/%s/%s\n' %(outdir,sample,eachC,eachID))
            	Step1Sh.write('mkdir -p %s/KEGG/%s/%s/%s\n' %(outdir,sample,eachC,eachID))
		Step1Sh.write('mkdir -p %s/KEGG/%s/%s/pathway_plot\n' %(outdir,sample,eachC))
		Step1Sh.write('mkdir -p %s/KEGG/%s/%s/pathway_plot/%s\n' %(outdir,sample,eachC,eachID))
		Step1Sh.write('mkdir -p %s/Reactome/%s/%s/%s\n' %(outdir,sample,eachC,eachID))
		Step1Sh.write('mkdir -p %s/TF/%s/%s/%s\n' %(outdir,sample,eachC,eachID))
		Step1Sh.write('mkdir -p %s/PPI/%s/%s/%s\n' %(outdir,sample,eachC,eachID))	
		Step1Sh.write('Rscript %s/bin/goenrich.R   --go %s  --clustergene %s/Cluster/%s/%s/%s.xls --diffresult %s/%s/outs/analysis/diffexp/%s/differential_expression.csv  --prefix %s/GO/%s/%s/%s/%s\n'  %(pipeline,go,outdir,sample,eachC,eachID,indir,sample,eachC,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('Rscript %s/bin/bar_plot.R  --stat %s/GO/%s/%s/%s/%s_GOenrich.txt --type GO --cutoff  pvalue  --prefix %s/GO/%s/%s/%s/%s_GO_bar\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('Rscript %s/bin/dot_plot  --stat %s/GO/%s/%s/%s/%s_GOenrich.txt --type GO --cutoff  pvalue  --prefix %s/GO/%s/%s/%s/%s_GO_dot\n\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		
		Step1Sh.write('Rscript %s/bin/kegg.R  --kegg  %s  --clustergene  %s/Cluster/%s/%s/%s.xls --diffresult %s/%s/outs/analysis/diffexp/%s/differential_expression.csv   --prefix %s/KEGG/%s/%s/%s/%s\n' %(pipeline,kegg,outdir,sample,eachC,eachID,indir,sample,eachC,outdir,sample,eachC,eachID,eachID))
	
		Step1Sh.write('Rscript %s/bin/bar_plot.R  --stat %s/KEGG/%s/%s/%s/%s_KEGGenrich.txt --type KEGG --cutoff  pvalue  --prefix %s/KEGG/%s/%s/%s/%s_kegg_bar\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('Rscript %s/bin/dot_plot  --stat %s/KEGG/%s/%s/%s/%s_KEGGenrich.txt --type KEGG --cutoff  pvalue  --prefix %s/KEGG/%s/%s/%s/%s_kegg_dot\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
	
		Step1Sh.write('Rscript %s/bin/kegg_pathway_plot  --clustergene %s/Cluster/%s/%s/%s.xls  --enrich %s/KEGG/%s/%s/%s/%s_KEGGenrich.txt  --kegg %s --species %s  --keggid %s   --keggdir %s --outdir %s/KEGG/%s/%s/pathway_plot/%s\n' %(pipeline,outdir,sample,eachC,eachID,outdir,sample,eachC,eachID,eachID,kegg,abbr,keggid,keggdir,outdir,sample,eachC,eachID))
		Step1Sh.write('python %s/bin/kegg_pathway_html --cpname %s --enrich %s/KEGG/%s/%s/%s/%s_KEGGenrich_significant.txt --pathdir %s/KEGG/%s/%s/pathway_plot/%s\n\n' %(pipeline,eachID,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID))
		Step1Sh.write('cd  %s/KEGG/%s/%s/pathway_plot/%s\n' %(outdir,sample,eachC,eachID))
		Step1Sh.write('python %s/bin/exact_keggpathway_detail --outdir  %s/KEGG/%s/%s/pathway_plot/%s --file  %s/Cluster/%s/%s/%s.xls\n' %(pipeline,outdir,sample,eachC,eachID,outdir,sample,eachC,eachID))
		Step1Sh.write('python %s/bin/get_KEGG_ID_Entrez_ID_for_identify --input %s/KEGG/%s/%s/%s/%s_KEGGenrich.txt  --out %s/KEGG/%s/%s/%s/add.%s.identify.xls  --species %s --dir  %s/KEGG/%s/%s/%s\n\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID,species,outdir,sample,eachC,eachID))
		
		Step1Sh.write('cd %s/KEGG/%s/%s/%s\n' %(outdir,sample,eachC,eachID))
		Step1Sh.write('python %s/bin/kegg_web_all/pathway_annotation_flow_parallel_annotationfault_tolerant_noref --table  %s/KEGG/%s/%s/%s/add.%s.identify.xls  --diff  %s/Cluster/%s/%s/%s.xls --abbr %s\n\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,abbr))
		Step1Sh.write('mv %s/KEGG/%s/%s/%s/add.%s.identify.xls_rendered_html_detail.html  %s/KEGG/%s/%s/%s/%s.html\n' %(outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))			

		Step1Sh.write('Rscript %s/bin/Reactome --diffgene %s/Cluster/%s/%s/%s.xls --diffresult %s/%s/outs/analysis/diffexp/%s/differential_expression.csv  --abbr %s --prefix %s/Reactome/%s/%s/%s/%s\n' %(pipeline,outdir,sample,eachC,eachID,indir,sample,eachC,abbr,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('Rscript %s/bin/dot_plot --stat %s/Reactome/%s/%s/%s/%s_Reactome_enrich.txt --type Reactome --cutoff padj --prefix  %s/Reactome/%s/%s/%s/%s_Reactome_dot\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('Rscript  %s/bin/bar_plot.R --stat %s/Reactome/%s/%s/%s/%s_Reactome_enrich.txt --type Reactome --cutoff padj --prefix %s/Reactome/%s/%s/%s/%s_Reactome_bar\n' %(pipeline,outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('python %s/bin/EntrezID_to_ensenmbleID.py --input %s/Reactome/%s/%s/%s/%s_Reactome_enrich.txt --species %s --out  %s/Reactome/%s/%s/%s/%s_Reactome_enrich_trans.txt\n' %(pipeline,outdir,sample,eachC,eachID,eachID,species,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('python %s/bin/EntrezID_to_ensenmbleID.py --input %s/Reactome/%s/%s/%s/%s_Reactome_enrich_significant.txt --species %s --out  %s/Reactome/%s/%s/%s/%s_Reactome_enrich_significant_trans.txt\n'  %(pipeline,outdir,sample,eachC,eachID,eachID,species,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('mv %s/Reactome/%s/%s/%s/%s_Reactome_enrich_trans.txt %s/Reactome/%s/%s/%s/%s_Reactome_enrich.txt\n'  %(outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('mv %s/Reactome/%s/%s/%s/%s_Reactome_enrich_significant_trans.txt  %s/Reactome/%s/%s/%s/%s_Reactome_enrich_significant.txt\n' %(outdir,sample,eachC,eachID,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('%s/bin/get_tf_anno --tf %s --diffgene  %s/Cluster/%s/%s/%s.xls  --outfile  %s/TF/%s/%s/%s/%s_tf.xls\n'  %(pipeline,tf,outdir,sample,eachC,eachID,outdir,sample,eachC,eachID,eachID))
		Step1Sh.write('%s/bin/PPI --ppi %s  --taxon %s  --stringdb /NJPROJ1/RNA/database/string/%s  --diffgene %s/Cluster/%s/%s/%s.xls --prefix  %s/PPI/%s/%s/%s/%s\n' %(pipeline,ppi,taxon,taxon,outdir,sample,eachC,eachID,outdir,sample,eachC,eachID,eachID))

Step1Sh.close()
os.system('sh '+root_dir+'/'+sample+'_enrich_step2.sh')
#	f1.write('cd %s\n' %(dir))
#	f1.write('python %s/bin/Enrich.py --species %s --dir %s --sample %s\n' %(pipeline,species,dir,eachS))

#	f1.close()
#	os.system('qsub -V -cwd -l vf=2G,p=2  run_'+eachS+'_step1.sh')
#	os.chdir('..')
