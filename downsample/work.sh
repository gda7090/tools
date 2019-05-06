#software/miniconda3/lib/R/bin/Rscript downsample.R A_4.specifc.clones.txt downsampled_A_4.specifc.clones.txt 2 46472 2
le pre_normalize.specific_clone.list |perl -ne 'chomp;$smp=$_;open(IN,$_);<IN>;$sum=0;while(<IN>){$c=(split/\t/,$_)[1];$sum+=$c};print "$smp\t$sum\n"' >sum.list
sort -k2 -n sum.list #取最小数据量值26480
le pre_normalize.specific_clone.list |perl -ne 'chomp;$_=~/(02.mix.*)\/(.*)/;chomp($d=`pwd`);print "mkdir -p $d/$1\n cd $d/$1\n software/miniconda3/lib/R/bin/Rscript $d/downsample.R $_ $d/$1/$2 2 26480 5\n\n"' >down.sh
#  perl super_worker.pl --qalter --cyqt 1 --maxjob 200 --sleept 600 --resource 5G  down.sh  -splits '\n\n' --prefix downs & 
