le pre_normalize.specific_clone.list |perl -ne 'chomp;$smp=$_;open(IN,$_);<IN>;$sum=0;while(<IN>){$c=(split/\t/,$_)[1];$sum+=$c};print "$smp\t$sum\n"' >sum.list
