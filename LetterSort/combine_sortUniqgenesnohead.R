args <- commandArgs(T)
if(length(args) < 2){
    cat("usage: <input: /fullPath/to/meanAdds.list> <output: combine.xls>\n")
    cat ("Example: /NJPROJ2/MICRO/PROJ/yangfenglong/software/miniconda3/lib/R/bin/Rscript /path/to/meanAdds.list  combine.xls\n")
    quit("no")
}


library(tidyverse)
lst<-read_lines(args[1])
tb1 <- read.table(lst[1],blank.lines.skip=T,sep="\t",fill =T)
	tb1<-tb1[tb1[,1]!="",] 


Fibonacci_bind_cols <- function(lst){
	tb1 <- read.table(lst[1],blank.lines.skip=T,sep="\t",fill =T)
	tb1[,1]<-as.character(tb1[,1])
	tb1<-tb1[tb1[,1]!="",] #del the blank rows
	reorder <- order(tb1[,1])
	tb1[reorder,] -> tb1
	for (i in 2:length(lst)){
		nrow1 <- nrow(tb1)
		tb2 <- read.table(lst[i],blank.lines.skip=T,sep="\t",fill =T)
		tb2[,1]<-as.character(tb2[,1])
		tb2 <- tb2[tb2[,1]!="",]
		nrow2 <- nrow(tb2)
		reorder <- order(tb2[,1])
		tb2[reorder,] -> tb2
	  	if(nrow1>nrow2){
		    tb2[(nrow2+1):nrow1,]<-""
		}else if(nrow1<nrow2){
	  		tb1[(nrow1+1):nrow2,]<-""
		}
	  	tb1 <- bind_cols(tb1,tb2)
	}
	return(tb1)
}

final_bind_cols <- Fibonacci_bind_cols(lst)
write_tsv(final_bind_cols,path=args[2],col_names=F)
