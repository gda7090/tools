args <- commandArgs(T)
if(length(args)<2){
    cat ("Example:  Rscript downsample.R ori.table downsampled.table coln nn dsn
: downsample the <coln> column of ori.table to <nn> zizefor <dsn> times to generate downsample.table\n")
    quit("no")
}

library(tidyverse)
down1sample <- function(x,coln,nn,dsn){
    # x是样本的矩阵，它会每一列样本都算一个加和然后取最小的（nn）做均一化
    # coln是均一化第几列
    # dsn是抽样次数,做几遍dowsample的意思，最后取的平均值
    # nn <- min( apply(x,2,sum) ) #nn min
  for ( j in 1:dsn ){
    z  <- data.frame(GENEID=rownames(x))
    rownames(z) <- rownames(x)
    initv <- rep(0,nrow(z))
    y <- aggregate(rep(1,nn),list(sample(rep(rownames(x),x[,coln-1]),nn)),sum)
    na <- names(x)[coln-1] 
    names(y) <- c("GENEID",na)
    k <- intersect(rownames(z),y$GENEID)
    z[k,na] <- y[k,na]
    z[is.na(z[,na]),na] <- 0
    
    ds <- if ( j == 1 ) z[,-1] else ds + z[,-1]
  }
  ds <- ds/dsn + .1
  return(round(ds))
}


downsample <- function(x,n,dsn){
    # x是所有样本的矩阵，它会每一列样本都算一个加和然后取最小的（nn）做均一化
    # n是过滤阈值，先过滤掉那些总丰度低于阈值的样本
    # dsn是抽样次数,做几遍dowsample的意思，最后取的平均值
  x <- round( x[,apply(x,2,sum,na.rm=TRUE) >= n], 0)
  nn <- min( apply(x,2,sum) )
  for ( j in 1:dsn ){
    z  <- data.frame(GENEID=rownames(x))
    rownames(z) <- rownames(x)
    initv <- rep(0,nrow(z))
    for ( i in 1:dim(x)[2] ){
      y <- aggregate(rep(1,nn),list(sample(rep(rownames(x),x[,i]),nn)),sum)
      na <- names(x)[i]
      names(y) <- c("GENEID",na)
      rownames(y) <- y$GENEID
      z[,na] <- initv
      k <- intersect(rownames(z),y$GENEID)
      z[k,na] <- y[k,na]
      z[is.na(z[,na]),na] <- 0
    }
    rownames(z) <- as.vector(z$GENEID)
    ds <- if ( j == 1 ) z[,-1] else ds + z[,-1]
  }
  ds <- ds/dsn + .1
  return(ds)
}

#main
x<- read.table(args[1],head=T,row.names=1,sep="\t")
#x<- as.data.frame(x)
out<-args[2] #output downsampled table
coln<-as.numeric(args[3]) #column number to downsample
nn<-as.numeric(args[4]) #min data size
dsn<-as.numeric(args[5]) #sample times

downedCol<-down1sample(x,coln,nn,dsn)
x[,coln-1]<-downedCol
output<-x[x[,coln-1]!=0,]
tb<-as.tibble(output)
tb<- add_column(tb,cloneId=rownames(output), .before = 1)
#write.table(file=out,x=output,row.names=T,quote=F,sep="\t")       
write_tsv(path=out,x=tb)
