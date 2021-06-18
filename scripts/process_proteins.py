#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################
# Author:				YeXiaNingYue
# Description:				-h
# Time:				2020年12月08日	 Tuesday
###########################################################
'''
根据蛋白序列和keg表，把二者整合起来
考虑到有些表的大小写不一致，这边可以处理,就是全部大写
'''
import  argparse
import re
import gzip

def get_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--org", metavar='org', type=str, help='org')
    parser.add_argument("--pep", metavar='pep', type=str, help='file of protein with fasta format')
    parser.add_argument("--keg", metavar='keg', type=str, help='file of kegs')
    parser.add_argument('--out', metavar='out', type=str, help='output file')
    args = parser.parse_args()
    return args

def check_files(files):
    for file_ in files:
        try:
            f = open(file_, 'r')
            f.close()
        except:
            print(f"{file_} is not exists")
            exit(0)

def parse_keg(file_keg):
    '''
    将keg存成字典{gene: ko, gene2: ko2, ...}
    '''
    gene_ko = {}
    f = open(file_keg, 'r')
    for line in f:
        if line[0]  != "D":
            continue
        else:
            try:
                gene,ko = re.search("D\s+(.*?)\s+.*\t(K\d{5})", line.strip()).group(1,2)
                gene_k = re.sub(r"\W", "", gene)
                gene_k = gene_k.upper()
            except:
                continue
            # if one protein have tow different ko, script will get error.
            if gene_ko.get(gene_k) and gene_ko.get(gene_k)[0] != ko:
                print(f"Fatal Error: In file {file_keg} \033[41;37m{gene}:{ko} is existed\033[0m, please check this script or update it.!!!!!!!!!!!")
                exit(127)
            gene_ko[gene_k] = [ko,gene]
    f.close()
    return gene_ko

def match_ko(str_org, name, gene, gene_ko, f_out):
    '''idk: ID-key'''

    if name == "" or name == None:
        return 0

    ids = {}
    id_ = ""

    if "locus_tag=" in name:
        id_ = re.search("locus_tag=(.*?)]", name).group(1)
        idk = re.sub(r"\W", "", id_)
        idk = id_.upper()
        ids[idk] = id_
    if "db_xref=GeneID:" in name:
        id_ = re.search("db_xref=GeneID:(.*?)]", name).group(1)
        idk = re.sub(r"\W", "", id_)
        idk = id_.upper()
        ids[idk] = id_
    if "protein_id=" in name:
        id_ = re.search("protein_id=(.*?).\d+]", name).group(1)
        idk = re.sub(r"\W", "", id_)
        idk = id_.upper()
        ids[idk] = id_
    if "gene=" in name:
        id_ = re.search("gene=(.*?)]", name).group(1)
        idk = re.sub(r"\W", "", id_)
        idk = id_.upper()
        ids[idk] = id_
    id_ = re.search(">(.*?)\s+", name).group(1)
    idk = id_.upper()
    ids[idk] = id_

    for id_ in ids.keys():
        if gene_ko.get(id_):
            f_out.write(f">{str_org}:{gene_ko[id_][1]}|{gene_ko[id_][0]}\n{gene}")
            del gene_ko[id_]
            return 1
    #if id_ != "":
        #print(f"Warning: {str_org}:{ids[id_]} pep not match with keg")
    return 0

def open_file(file_):
    if re.search(".*.gz", file_):
        f = gzip.open(file_, 'rb')
    else:
        f = open(file_, 'rb')
    return f

def replace_name(str_org, file_pep, file_out, file_keg):
    gene_ko = parse_keg(file_keg) # 获取keg里面的gene -> ko 对应关系
    #f_pep = open_file(file_pep)
    f_pep = open(file_pep, 'r')
    f_out = open(file_out, 'w')
    last_name = ""
    gene = ""
    npep = 0
    npep_exists = 0
    nkeg = gene_ko.__len__()
    
    # 遍历蛋白序列
    for line in f_pep:
        #line = line.decode()
        if line[0] == ">":
            temp_n = match_ko(str_org, last_name, gene, gene_ko, f_out)
            gene = ""
            last_name = line.strip()
            npep += 1
            npep_exists += temp_n
        else:
            gene += line
    f_pep.close()
    f_out.close()
    residue_keg = gene_ko.__len__()
    #print(gene_ko)
    print(f"{str_org}\ttotal ko: {nkeg}\tmatch: {npep_exists}\ttotal protein: {npep}\tresidue ko: {residue_keg}")


def main(str_org, file_pep, file_keg, file_out):
    
    replace_name(str_org, file_pep, file_out, file_keg)



if __name__ == "__main__":

    args = get_args()

    check_files([args.pep, args.keg]) # 判断文件是否存在
    main(args.org, args.pep, args.keg, args.out)

