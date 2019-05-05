l |awk '{print $(NF-2)}'|grep gz|awk '{print "/NJPROJ2/MICRO/PROJ/yangfenglong/software/seqkit stat "$NF" >" $NF".seqkit_len.stat";}' >seqkit_len.stat.sh
qsub -cwd -l vf=5g,p=6 -V seqkit_len.stat.sh
