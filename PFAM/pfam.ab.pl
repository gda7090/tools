#!/usr/bin/perl
use strict;
use warnings;

my $file=shift;
my %pfam=();
open ANN,$file;
my $id;
my $name;
while(<ANN>){
	if(/^ACC\s+(PF\d{5}).*\n/){
		$id=$1;
	}
	elsif(/^DESC\s+(.*?)\n/){
		$name=$1;
	}
	elsif(/^LENG\s+\d+/){
		$pfam{$id}=$name;
	}
}

foreach(keys %pfam){
	print $_."\t".$pfam{$_}."\n";
}
