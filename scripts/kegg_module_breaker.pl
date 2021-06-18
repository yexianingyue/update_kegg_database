#!/usr/bin/perl
use warnings;
use strict;
die "Usage: perl $0 [module.definition] [module.definition.reaction]\n" unless @ARGV == 2;
my ($in_f, $out_f) = @ARGV; die "Overlap In-Output...\n" if $in_f eq $out_f;
open IN, $in_f or die $!;
open OT, ">$out_f" or die $!;
while(<IN>){
	chomp;
	my ($module, $string) = split /\t+/;
	my %path = ();
	$path{0} = $string;

	while(1){
		my @k = sort keys %path;
		my $k_num = 0;
		foreach my $k(@k){
			if($path{$k} =~ /^(.*)\((.*?)\)(.*)$/){
				my ($a,$b,$c) = ($1,$2,$3);
				delete $path{$k};
				my @b = split /,/,$b;
				for my $i(0..$#b){
					$path{$k.$i} = $a.$b[$i].$c;
				}
				last;
			}elsif($path{$k} =~ /,/){
				my @b = split /,/,$path{$k};
				delete $path{$k};
				for my $i(0..$#b){
					$path{$k.$i} = $b[$i];
				}
				last;
			}
			$k_num++;
		}
		last if @k == $k_num;
	}
	my %uniq = ();
	foreach (sort keys %path){
		print OT "$module\t$_\t$path{$_}\n" unless exists $uniq{$path{$_}};
		$uniq{$path{$_}}++;
	}
}
close IN;
close OT;
print STDERR "Program End...\n";
############################################################
