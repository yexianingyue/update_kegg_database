# KEGG UPDATE
## 自己下载 网页源码 “https://www.kegg.jp/kegg/catalog/org_list.html”

```sh
wget -O "org_list.html" "https://www.kegg.jp/kegg/catalog/org_list.html"
wget -O "ko00001.keg" "https://www.kegg.jp/kegg-bin/download_htext?htext=ko00001.keg"   # download 改成get就是网页浏览
wget -O "ko00002.keg" "https://www.kegg.jp/kegg-bin/download_htext?htext=ko00002.keg"
wget -O "br08610.keg" "https://www.kegg.jp/kegg-bin/download_htext?htext=br08610.keg&format=htext&filedir="
```

## 生成profile表
```sh
le org_list.html  | perl -e '$stat=0;while(<>){chomp;if($_=~/  <td align.*id="(.*)">/){$stat=1;$org=$1;next};if ($stat == 1){if ($_=~/  <td align=left.*href='"'"'\/dbget-bin\/www_bfind\?(.*?)'"'"'>(.*)<\/a><\/td>/){$org_ful="$1\t$2";next};if($_=~/.*ftp:\/\/ftp.*/){$_=~/(ftp:.*)'"'"'/;print "$org\t$org_ful\t$1\n";$stat=0;$org="",$org_ful="";next}}}' > KEGG.org
```

## 生成下载蛋白序列的shell， 以及没有ko对应关系的物种，不管它，自己好奇想看也行
``` sh
le KEGG.org | perl -e 'open out1, ">download_protein.sh";open out2, ">download.kegg.ko.sh";while(<>){chomp;@l=split/\t/; if ($l[1] eq ""){print "$l[0]\n"; next};@s=split("/", $l[3]); print out1 "wget --timeout 60 --tries 10 -O \"./NCBI-proteins/$l[0].pep.fasta.gz\"  \"$l[3]/$s[-1]_translated_cds.faa.gz\"\|\| rm \"./NCBI-proteins/$l[0].pep.fasta.gz\"\n"; print out2 "wget --timeout 60 --tries 10 -O  \"KEGG-KO/$l[0]00001.keg\" \"https://www.kegg.jp/kegg-bin/download_htext?htext=$l[0]00001.keg&format=htext&filedir=\" \|\| rm \"KEGG-KO/$l[0]00001.keg\" \n"}' > no_ko_org.list

le br08610.keg  | perl -e '$status=0;while(<>){if ($_=~/TAX:\d+\]/){$status=1;$_=~/TAX:(\d+)\]/;$tax=$1;next};if ($status == 1){@l=split/\s+/;print "$l[1]\t$tax\n" if $l[1] ne $tax;$status=0}}' > KEGG.taxo

```

## 下载

## 创建必要的目录
```sh
mkdir KO-proteins modules.map NCBI-proteins KEGG-KO
```


## 需要手动下载的keg和蛋白序列
```sh
lem
wget -O ./NCBI-proteins/lem.pep.fasta.gz "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/002/355/975/GCA_002355975.1_ASM235597v1/GCA_002355975.1_ASM235597v1_translated_cds.faa.gz"
wget -O KEGG-KO/lem00001.keg "https://www.kegg.jp/kegg-bin/download_htext?htext=lem00001.keg&format=htext&filedir="

dosa
wget -O ./NCBI-proteins/dosa.pep.fasta.gz "https://rapdb.dna.affrc.go.jp/download/archive/irgsp1/IRGSP-1.0_protein_2021-05-10.fasta.gz"
wget -O KEGG-KO/dosa00001.keg "https://www.kegg.jp/kegg-bin/download_htext?htext=dosa00001.keg&format=htext&filedir="

pfd
wget -O ./NCBI-proteins/pfd.pep.fasta.gz "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/149/795/GCA_000149795.1_ASM14979v1/GCA_000149795.1_ASM14979v1_translated_cds.faa.gz"
wget -O KEGG-KO/pfd00001.keg "https://www.kegg.jp/kegg-bin/download_htext?htext=pfd00001.keg&format=htext&filedir="

pfh
wget -O ./NCBI-proteins/pfh.pep.fasta.gz "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/149/665/GCA_000149665.2_ASM14966v2/GCA_000149665.2_ASM14966v2_translated_cds.faa.gz"
wget -O KEGG-KO/pfh00001.keg "https://www.kegg.jp/kegg-bin/download_htext?htext=pfh00001.keg&format=htext&filedir="


smin
wget -O ./NCBI-proteins/smin.pep.fasta.gz "https://marinegenomics.oist.jp/symb/download/symbB.v1.2.augustus.prot.fa.gz"
wget -O KEGG-KO/smin00001.keg "https://www.kegg.jp/kegg-bin/download_htext?htext=smin00001.keg&format=htext&filedir="
```

### 下载数据
```sh
nohup parallel  -j 9 --joblog download_protein.run.log  < download_protein.sh  > download_protein.log 2>&1 &
nohup parallel  -j 9 --joblog download.kegg.ko.run.log < download.kegg.ko.sh > download.kegg.ko.log 2>&1 &
```

#### 格式化蛋白序列
```sh
nohup cut -f 1 KEGG.org | parallel --joblog ko-proteins.run.log  -j 30 ./process_proteins.py --org {} --keg KEGG-KO/{}00001.keg --pep NCBI-proteins/{}.pep.fasta --out KO-proteins/{}.ko.fasta > log&
```

#### 生成module通路
```sh
grep "^D" ko00002.keg| perl -ne 'chomp;@l=split/\s+/;print "wget --timeout 60 --tries 10  -O ./modules.map/$l[1].html \"https://www.genome.jp/dbget-bin/www_bget?md:$l[1]\"\n"' |  parallel -j 32  --joblog ./modules.run.log &
parallel --retry-failed --joblog modules.run.log
```
#### 生成module的通路，用于计算module的完整性
```sh
ls modules.map/*.html | parallel --plus  -j 32 sh modules.map.parse.sh {}  {/..} > modules.map.list # 生成map 列表
sed 's/<wbr>//g' modules.map.list | sed 's/ --//g' | sed 's/-- //g' > modules.map.list.f;mv modules.map.list.f modules.map.list
./kegg_module_breaker.pl modules.map.list modules.map.reaction
```

#### 这一步可以不做
```sh
cat modules.map.reaction  backup/modules.map.list.out_of_print.reaction > modules.map.reaction.merge
```
记得备份`cp ko00002.keg ko00002.keg.bac`。手动删除`ko00002.keg`的最后几行[以`！`或`#`开头的行],然后`cat ko00002.keg backup/ko00002.keg.out_of_print >> ko00002.keg.merge`
### 整理ko00002.keg
```sh
le ko00001.keg | perl -ne 'chomp; next if !/^D\s+(K\d+)/;$_=~/^D\s+(K\d+)\s+(.*)/;print "$1\t$2\n"' | sort -k 1,1 -u > ko.desc
cat modules.map.list backup/modules.map.list.out_of_print | perl -e '%ko;open I, "ko.desc";while(<I>){chomp;@l=split/\t/;$ko{$l[0]}=$l[1]};%h;while(<>){chomp;@l=split/\t/;while($l[1]=~/(K\d{5})/g){$h{$l[0]}.="E        $1\t$ko{$1}\n"}};open M, "ko00002.keg.merge";while(<M>){chomp;next if(/^E\s+K\d+/);if(!/^D\s+M\d+/){print "$_\n"}else{print "$_\n";$_=~/^D\s+(M\d{5})/;print "$h{$1}"} }'  > ko00002.keg
```

## 整理映射关系
```sh

```


2：删除
```sh
find . -name "*" -type f -size 0c | xargs -n 1 rm -f
```
用这个还可以删除指定大小的文件，只要修改对应的 -size 参数就行

## 其他

`parallel` 是个命令行下可以并行运行的软件，涉及到它的命令行，都可以改用为单线程线性下载。没有必要非它不可。
