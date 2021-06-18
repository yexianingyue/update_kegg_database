perl -e '$stat=0;open I, $ARGV[0];while(<I>) {if($stat==1){$_=~/.*hidden">(.*)<br>/;print "$ARGV[1]\t$1\n";exit}else{if (/Definition/){$stat=1;next}}}' $1 $2
