#!/usr/bin/perl -w
use strict;
my $chrlist=shift;
open (IN,"$chrlist") || die $!;
open (OUT,"> karyotype.txt") || die $!;
my @colour=("chr1","chr2","chr3","chr4","chr5","chr6","chr7","chr8","chr9","chr10","chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19","chr20","chr21","chr22","chr1","chr2","chr3","chr4","chr5","chr6","chr7","chr8","chr9","chr10","chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19","chr20","chr21","chr22","chr1","chr2","chr3","chr4","chr5","chr6","chr7","chr8","chr9","chr10","chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19","chr20");
my $i=0;
while(<IN>){
	chomp;
	my @line=split(/\s+/,$_);
	if($i%2){
		print OUT "chr - $line[0] $line[0] 0 $line[1] $colour[$i]\n";
	}else{
		print OUT "chr - $line[0] $line[0] 0 $line[1] $colour[$i]\n";
	}
	$i++;
}
close IN;
close OUT;
