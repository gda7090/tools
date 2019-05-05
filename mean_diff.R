args<-commandArgs(T)
a<-read.table(args[1], head=T,row.names=1,sep="\t",check.names=F)            
df<-data.frame(geneid=row.names(a), mean_diff=a[,1]-a[,3], pvalue=a[,5], lower=a[,ncol(a)-1], uper=a[,ncol(a)])
write.table(x=df,quote=F,file=args[2],row.names=F,sep="\t")   
