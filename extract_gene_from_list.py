import sys
from Bio import SeqIO
all_gene_file=sys.argv[1].strip()
gene_list=sys.argv[2].strip()
out=sys.argv[3]
all_gene=open(all_gene_file,'r')
genelist=open(gene_list,'r').readlines()
out_file=open(out,'w')
list=[]
for each_l in genelist:
    each=each_l.strip()
    list.append(each)
for seq_record in SeqIO.parse(all_gene,"fasta"):
    id=seq_record.id
    seq=seq_record.seq
    if id in list:
        out_file.write(">"+str(id)+"\n"+str(seq)+"\n")
out_file.close()



