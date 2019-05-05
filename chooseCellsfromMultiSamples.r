count <- read.delim("../ENSMUSG00000025270filt.m1_S2_S3_gene_bar.csv",header=TRUE,sep=',',row.names=1)

subcount<-count[,match(colnames(count)[grep(pattern='1',colnames(count))],colnames(count))]
B_bcs<-colnames(subcount_B<-subcount[,which(subcount[which(rownames(subcount)=="ENSMUSG00000020717"),]>0 & subcount[which(rownames(subcount)=="ENSMUSG00000025608"),]>0)])
B_bcs_new<-merge(B_bcs,"S2Pecam1Podxl")
colnames(B_bcs_new)<-c("sample","group")
write.table(B_bcs_new,file=("S2_Pecam1_Podxl_barcode.csv"),sep='\t',quote=F,row.names=F)
subcount<-count[,match(colnames(count)[grep(pattern='2',colnames(count))],colnames(count))]
B_bcs<-colnames(subcount_B<-subcount[,which(subcount[which(rownames(subcount)=="ENSMUSG00000020717"),]>0 & subcount[which(rownames(subcount)=="ENSMUSG00000025608"),]>0)])
B_bcs_new<-merge(B_bcs,"S3Pecam1Podxl")
colnames(B_bcs_new)<-c("sample","group")
write.table(B_bcs_new,file=("S3_Pecam1_Podxl_barcode.csv"),sep='\t',quote=F,row.names=F)

subcount<-count[,match(colnames(count)[grep(pattern='1',colnames(count))],colnames(count))]
B_bcs<-colnames(subcount_B<-subcount[,which(subcount[which(rownames(subcount)=="ENSMUSG00000035783"),]>0 & subcount[which(rownames(subcount)=="ENSMUSG00000001435"),]>0)])
B_bcs_new<-merge(B_bcs,"S2Acta2Col18a1")
colnames(B_bcs_new)<-c("sample","group")
write.table(B_bcs_new,file=("S2_Acta2_Col18a1_barcode.csv"),sep='\t',quote=F,row.names=F)
subcount<-count[,match(colnames(count)[grep(pattern='2',colnames(count))],colnames(count))]
B_bcs<-colnames(subcount_B<-subcount[,which(subcount[which(rownames(subcount)=="ENSMUSG00000035783"),]>0 & subcount[which(rownames(subcount)=="ENSMUSG00000001435"),]>0)])
B_bcs_new<-merge(B_bcs,"S3Acta2Col18a1")
colnames(B_bcs_new)<-c("sample","group")
write.table(B_bcs_new,file=("S3_Acta2_Col18a1_barcode.csv"),sep='\t',quote=F,row.names=F)

subcount<-count[,match(colnames(count)[grep(pattern='1',colnames(count))],colnames(count))]
B_bcs<-colnames(subcount_B<-subcount[,which(subcount[which(rownames(subcount)=="ENSMUSG00000029231"),]>0 & subcount[which(rownames(subcount)=="ENSMUSG00000027750"),]>0)])
B_bcs_new<-merge(B_bcs,"S2PdgfraPostn")
colnames(B_bcs_new)<-c("sample","group")
write.table(B_bcs_new,file=("S2_Pdgfra_Postn_barcode.csv"),sep='\t',quote=F,row.names=F)
subcount<-count[,match(colnames(count)[grep(pattern='2',colnames(count))],colnames(count))]
B_bcs<-colnames(subcount_B<-subcount[,which(subcount[which(rownames(subcount)=="ENSMUSG00000029231"),]>0 & subcount[which(rownames(subcount)=="ENSMUSG00000027750"),]>0)])
B_bcs_new<-merge(B_bcs,"S3PdgfraPostn")
colnames(B_bcs_new)<-c("sample","group")
write.table(B_bcs_new,file=("S3_Pdgfra_Postn_barcode.csv"),sep='\t',quote=F,row.names=F)


