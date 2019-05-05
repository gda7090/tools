suppressPackageStartupMessages(library("optparse"))

option_list <- list(
		make_option("--infilepath", action="store",default=NULL, help="The dirctory of Evenabs.mat, look like: ./Project/03.Make_OTU/otu97/Evenabs"),
		make_option("--group", action="store",default=NULL, help="The file contain group infomation ,without header"),
		make_option("--vs", action="store", default=NULL, help="The Comparison group info,look like: Contrast,Case;Contrast,Case;Contrast,Case..."),
		make_option("--outdir", action="store",,default="./", help="The output dirctory,  [default %default]"),
		make_option("--threshold", type="double",default=0.05, help="The cutoff value or sig [default %default]"),
		make_option("--Vslist", action="store",default=NULL, help="The Comparison group info,look like: a\tb\nc\tb"),
        make_option("--method", action="store",default="t", help="t or wilcox")
#make_option("--correlation", type="integer",default=1, help="Correlation to use: 1=pearson, 2=spearman, 3=kendall [default %default]"),
#make_option("--rmode", action="store_true",default=FALSE, help="Mode: TRUE=R mode, FALSE=Q mode [default %default]")
)

#get command line options
opt<-parse_args(OptionParser(usage="%prog [options] file\n", option_list=option_list))
if(is.null(opt$infilepath) ||is.null(opt$group) ){
	cat ("Use  %prog -h for more help info\nThe author: wangxiaohong@novogene.cn\n")
	quit("no")
}

#args<-commandArgs(T)
#if(length(args)<3){
#	cat("[usage:] <Dir:/otu97/Evenabs/> <greoup.info> <Contral_GroupAname,Case_GroupBname;Contral_GroupAname,Case_GroupCname;...> <Dir:outdir> \n")
#	cat ("Example:  plot_aplhaindex.R Report01/03.Make_OTU/otu97/Evenabs/ group.info GroupAname,GroupBname... outdir\n")
#	quit("no")
#}

method = opt$method
infilepath<-opt$infilepath
matfiles<-list.files(infilepath)
group.file<-opt$group
outdir<-paste(opt$outdir,"/",sep="")

if(!is.null(opt$Vslist)&&file.exists(opt$Vslist)){
	#vslistdata<-read.table(opt$Vslist,sep="\t")
    vslistdata<-read.table(opt$Vslist)#add by hanyuqiao
	vslistdata<-as.matrix(vslistdata)
	pnu<-dim(vslistdata)[1]
	for(i in 1:pnu){
		if(is.null(opt$vs)){
			opt$vs<-paste(as.vector(vslistdata[i,]),collapse=",")
		}else{
			opt$vs<-paste(opt$vs,paste(as.vector(vslistdata[i,]),collapse=","),sep=";")
		}
	}
}else{#auto analyse all group add by hanyuqiao
	vslistdata<-read.table(group.file,sep="\t")
	vslistdata<-as.matrix(vslistdata)
	allgroups<-unique(vslistdata[,2])
	pnu<- length(allgroups)[1]
	for(i in 1:(pnu-1)){
		for(j in (i+1):pnu){
			if(is.null(opt$vs)){
				opt$vs<- paste(as.vector(allgroups[i]),as.vector(allgroups[j]),sep=",")
			}else{
				opt$vs<-paste(opt$vs,paste(as.vector(allgroups[i]),as.vector(allgroups[j]),sep=","),sep=";")

			}
		}
	}	

}
if(!file.exists(outdir)){
	dir.create(outdir)
}

groupnames<-unlist (strsplit(opt$vs,",|;",fixed=F))
Pairs<-unlist(strsplit(opt$vs,";",fixed=T))
#source ("/BJWORK/GR/wangxiaohong/Script/MetaStat.Test/Step02.Test/ddaf3.R") ##
source("/NJPROJ2/MICRO/share/Full_length_16S_pipeline/Full_length_16S_pipeline_V1.0/lib/05.Statistic/lib/t.wilcox.R.lib/t.test.sub.R") #add by hanyuqiao
Level<-c("class","family","genus","order","phylum" ,"species")
names(Level)<-c("c","f","g","o","p","s")
group<-read.table(group.file,sep="\t",header=F)
#group.all<-group[,which(group[,2] %in% unlist(groupnames))==T]
group.all<-group[which(group[,2] %in% groupnames),][,1]
temp.outdir<-outdir

for( i in 1:length(matfiles)){
	outdir<-temp.outdir
	cfgops<-substr(matfiles[i], 11, 11)

	if(cfgops=="k"){
		next
	}
    if(cfgops=="r"){next}
	outdir<-paste(outdir,Level[cfgops],sep="") #Level[cfgops] like " otu_table.c.absolute.mat ",so11 corresponding to  o s f p ...
	if (!file.exists(outdir)){
		dir.create(outdir)
	}
	T.level<-read.table(paste(infilepath,"/",matfiles[i],sep=""),head=T,sep="\t", row.names=NULL)
	row.names(T.level)<-T.level[,dim(T.level)[2]]
	T.level[,1]<-NULL
	T.level[,dim(T.level)[2]]<-NULL
	data<-T.level
	#colnames(data)<-colnames(T.level)[2:length(T.level[1,])]
	select.data<-colnames(data) %in% group.all
	select.name<-colnames(data)[select.data]
	select.data.file<-paste(outdir,"/",matfiles[i],sep="")
	data<-data[,select.data]	
#	data <- data[which(apply(data ,1,sum)!=0),] #过滤全0行

    write.table(data, select.data.file,quote = FALSE,sep="\t")
	

	for(p in 1:length(Pairs)){
		pair<-unlist (strsplit(Pairs[p],",|;",fixed=F))
		#pair.data.file<-paste(outdir,"/",pair.file.name,".mat",sep="")
		group1.dat<-which(group[,1] %in% select.name)[which(group[which(group[,1] %in% select.name),2]==pair[1])]
		group1<-which(select.name %in% group[group1.dat,1])
		##group2<-which(group[which(group[,1] %in% select.name),2]==pair[2])
		group2.dat<-which(group[,1] %in% select.name)[which(group[which(group[,1] %in% select.name),2]==pair[2])]
		group2<-which(select.name %in% group[group2.dat,1])
		mark.group2<-length(group1)+1
		#group.pair<-group[,which(group[,2] %in% pair)==T]
		group.pair<-c(group1,group2)
		#q("no")
			
        if(length(group1)>2 & length(group2)>2){
		    perfix<-paste(pair,collapse="-vs-")
	    	pair.file.name<-paste(outdir,"/",perfix,sep="")
	    	test.file.name<-paste(pair.file.name,".test.xls",sep="")
	    	p.file.name<-paste(pair.file.name,".psig.xls",sep="")
	    	q.file.name<-paste(pair.file.name,".qsig.xls",sep="")
	    	write.table(data[,group.pair],paste(pair.file.name,".",cfgops,".mat",sep=""),quote = FALSE,sep="\t",col.names = NA)
            twosampledata=data[,group.pair]
            #delte two grous that each group has same abudance
            ncols = ncol(twosampledata)
            allsame=array(0, dim=c(0,ncols)); 
            for(k in 1:dim(twosampledata)[1]){
                if(  (length(unique(twosampledata[k, 1:(mark.group2-1)]))==1) & (length(unique(twosampledata[k, mark.group2:ncols]))==1) ){ #samples in group has same abundance 
                    temp = c(twosampledata[k,])
                    allsame = rbind(allsame,temp) #save as a file
                
                }
            }
            if(dim(allsame)[1]>0){
                allsame=as.data.frame(allsame)
                colnames(allsamefile)=colnames(twosampledata)
                write.table(allsame,file=paste(pair.file.name,".",cfgops,".mat.same.xls",sep=""),row.names = F,quote = FALSE,sep = "\t");
            }
            
		#cat (mark_group2,"\n")
		    detect_differentially_abundant_features(infile=select.data.file,group1,group2,g=mark.group2,output=test.file.name,output2=p.file.name,output3=q.file.name,pflag = NULL, threshold = 0.05, B = NULL, method=method, name1=pair[1], name2=pair[2])
        }
        #detect_differentially_abundant_features <- function(infile,group1,group2,g,output,output2,output3, pflag = NULL, threshold = NULL, B = NULL)
        #
		#cat (select.data.file,group1,group2,mark_group2,test.file.name,p.file.name,q.file.name,"\n\n")
	}
}

