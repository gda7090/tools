import os,argparse
from multiprocessing.dummy import Pool as ThreadPool
from time import sleep,ctime
import random
import sys

parser = argparse.ArgumentParser(description="\033[34mthe ThreadPool test of zhouwenyang\033[37m")
parser.add_argument('-g','--genelist',help="inputfile",required=True)
parser.add_argument('-b','--bamlist',help="inputfile",required=True)
parser.add_argument('-f','--method',help="input is  dot or area?",choices=['dot','area'],default='dot')
parser.add_argument('-k','--breadth',help="if --method =='dot', then the breadth of up and down",default=500,type=int)
parser.add_argument('-x','--thread',help="the number of ThreadPool ",default=5,type=int)
parser.add_argument('-o','--outpath',help="outputfile",required=True)
parser.add_argument('-p','--pos_info',help='Position Information',default=' ')
parser.add_argument('-r','--genome',help='Reference Genome, b37 or b38 or reference path',default='b37')
argv = parser.parse_args()

genelist=argv.genelist
bamlist=argv.bamlist
outpath=argv.outpath
genome_files = {
    'b37':'/NJPROJ2/CANCER/share/database/Genome/human/b37/human_g1k_v37_decoy.fasta',
    'b38':'/ifs/TJPROJ3/CANCER/share/Database/Genome/human_B38/human_B38.fa'
}

if os.path.exists(argv.genome):
    genome=argv.genome
elif argv.genome in genome_files.keys():
    genome=genome_files[argv.genome]
else:
    print 'The reference must be b37 or b38 or path.'
    sys.exit(1)
collist=['\033[35m','\033[34m','\033[31m','\033[37m','\033[32;4m','\033[33;4m','\033[33;4m','\033[0m','\033[4m','\033[4m','\033[5m']

def html_colored(input_html,out_html,color_ref = '#FF83FA', color_alt = 'lime',relative_pos = [101]):
	out = open(out_html,'w')
	ref_base = []
	i = 0
	for line in open(input_html):
		line = line.rstrip('\n')
		if i == 3:
			for m in range(len(line)):
				if line[m] in ['A','G','C','T','N','a','g','c','t','n']:
					begin_index = m
					break
			line_refs = line[begin_index:]
			for item in relative_pos:
				ref_base.append(line_refs[item-1])
			
		if i < 5:
			i += 1
			out.write(line+'\n')
			continue
		if len(line)==0 or line.startswith('_') or line.startswith('<'):
			out.write(line+'\n')
			continue
		flag_box = 0
		flag_index = 0
		flagx = 0
		strx = ''
		line_out = ''
		for m in range(len(line)):
			cc = line[m]
			line_out += cc
			if flagx == 1:
				flagx = 0
				continue
			if cc == '<':
				flag_box += 1
				continue
			if cc == '>':
				flag_box -= 1
				continue
			
			if m >= begin_index and flag_box == 0:
				flag_index += 1
				strx += cc
				if flag_index in relative_pos:
					n = relative_pos.index(flag_index)
					if cc != ' ':
						if cc.upper() == ref_base[n].upper():
							line_out = line_out[:-1] + '''<font style="background-color:%s">%s</font>'''%(color_ref,cc)
						else:
							line_out = line_out[:-1] + '''<font style="background-color:%s"><b>%s</b></font>'''%(color_alt,cc)
				
		out.write(line_out+'\n')
	out.close()


def getout(genename,bam):
	samplename=bam.split('/')[-1].split('.')[0]
	outfile=os.path.join(argv.outpath,genename,samplename,genename+samplename)
	return outfile

def path_cun(path):
	if not os.path.exists(path) :
		os.system('mkdir -p %s'%path)

def bam2html(paras):
	col=collist[random.randint(0,10)]
	bam,region,filename=paras
	name=bam.split('/')[-1].split('.')[0]
	print '%sI Start '%col,name,'at',region,' \033[37m'
	path_cun('/'.join(filename.split('/')[0:-1]))
	Code='''samtools view -h -b -S  %s %s > %s
samtools index %s
perl ExtractBam/code/bam2html.pl \\
	-r %s \\
	-d %s \\
	--range %s \\
	-o %s
'''%(bam,region,filename+'.bam',filename+'.bam',genome,bam,region,filename+'.html')
	open(filename+'.sh','w').write(Code)
	os.system('sh %s'%(filename+'.sh'))
	os.system('rm -rf %s '%(filename+'.sh'))
	# color
	if argv.breadth<100:
		print 'The breadth must be greater than 100.'
		sys.exit(1)
	html_colored(filename+'.html', filename+'.colored.html',relative_pos=[argv.breadth+1])
	print '%sI End '%col,name,'at',region,' \033[0m'
	
def run(fun,paras,cpu):
        pool=ThreadPool(cpu)
        pool.map(fun,paras)
        pool.close()
        pool.join()

if argv.method=='dot' :list={ each.split()[0]+':'+str(int(each.split()[1])-argv.breadth)+'-'+str(int(each.split()[1])+argv.breadth): '_'.join(each.split())   for each in open(argv.genelist,'r')}
if argv.method=='area' :list={ each.split()[0]+':'+each.split()[1]+'-'+each.split()[2]: '_'.join(each.split())   for each in open(argv.genelist,'r')}

bam_list=[each.strip() for each in open(argv.bamlist,'r')]
paras_list=[[a,b,getout(list[b],a)] for a in bam_list  for b in list]
run(bam2html,paras_list,argv.thread)

outdir = argv.outpath
gene_info_file = argv.pos_info
if os.path.exists(gene_info_file):
    if not os.path.exists(os.path.join(outdir,'result')):
        os.system('mkdir '+os.path.join(outdir,'result'))
    if not os.path.exists(os.path.join(outdir,'result','src')):
        os.system('mkdir '+os.path.join(outdir,'result','src'))
    os.system('cp -r %s %s'%(os.path.join(os.path.dirname(sys.argv[0]),'src','js_css') ,os.path.join(outdir,'result','src')))
    html = '''\
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"> 
<title>Gene Information</title>
<link rel="stylesheet" href="src/js_css/jq.css" type="text/css" media="print, projection, screen" />
<link rel="stylesheet" href="src/js_css/style.css" type="text/css" media="print, projection, screen" />
<script type="text/javascript" src="src/js_css/jquery-1.1.3.js"></script>
<script type="text/javascript" src="src/js_css/jquery.tablesorter.js"></script>
<script type="text/javascript" src="src/js_css/jquery.tablesorter.pager.js"></script>
<script type="text/javascript">
$(document).ready(function(){
	$(".table-00").tablesorter();
	$(".table-01").tablesorter();
	$("#ajax-append").click(function(){
		$.get("docs/assets/ajax-content.html",function(html) {
			// append the "ajax'd" data to the table body
			$(".table-01 > tbody").append(html);
			// let the plugin know that we made a update
			$(".table-01").trigger("update");
			// set sorting column and direction, this will sort on the first and third column
			var sorting = [[0,0],[2,0]];
			// sort on the first column
			$(".table-01").trigger("sorton",[sorting]);
		});
		return false;
	});
	// extend the default setting to always include the zebra widget.
	$.tablesorter.defaults.widgets = ['zebra'];
	// extend the default setting to always sort on the first column
	$.tablesorter.defaults.sortList = [[0,0]];
	// call the tablesorter plugin
	$(".table-02").tablesorter();
	$(".table-03").tablesorter({
		headers:{1:{sorter:false},2:{sorter:false}}
	}); 
	$(".table-04").tablesorter({widthFixed: true}).tablesorterPager({container: $("#pager")});
}); 		
</script>
</head>
<body>

<div id="main">
<br>
<table cellspacing="1" class="tablesorter table-01" style="table-layout:fixed;word-break:break-all; word-wrap:break-all;">
'''

    i = 0    
    for line in open(gene_info_file):
        if i == 0:
            i += 1
            array_title = line.strip().split('\t')+['link']
            html += '<thead><tr><th>' + '</th><th>'.join(array_title) + '</th></tr></thead>\n'
            html += '<tfoot><tr><th>' + '</th><th>'.join(array_title) + '</th></tr></tfoot>\n<tbody>\n'
            continue
        array = line.strip().split('\t') 
        dir1 = '_'.join([array[1],array[2],array[3]])
        dir2 = array[0]
        file1 = dir1+dir2+'.colored.html'
        file1_path = os.path.join(outdir,dir1,dir2,file1)
        assert not os.system('cp %s %s'%(file1_path,os.path.join(outdir,'result','src')))
        array.append('''<a href="src/%s" target="_blank">See Bam</a>'''%file1)
        html += '<tr><td>' + '</td><td>'.join(array) + '</td></th>\n'
        
    html +='''
</tbody>
</table>
</div>
</body>
</html>
'''
    open(os.path.join(outdir,'result','index.html'),'w').write(html)
    os.system('cd %s && tar zcvf result.tar.gz index.html src/ 1>/dev/null && mv result.tar.gz ..'%os.path.join(outdir,'result'))
