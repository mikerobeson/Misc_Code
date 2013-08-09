#!/usr/bin/env python
# file: prep_silva_taxonomy_file.py
# by Mike Robeson Feb 2013
# This converts a raw taxonomy file into a qiime / rdp compatable
# taxonomy file. Input is taxonomy file from 'prep_silva_data.py'

from string import maketrans

def load_taxonomy_to_dict(taxonomy):
    """reads in the taxonomy file.
        in the form of 'seqID \t taxonomy'
    returns dict {seqID : taxonomy}
    """
    d = {}
    for line in taxonomy:
        seqID,taxonomy = line.split('\t',1)
        d[seqID] = taxonomy.strip()
    return d
    
def get_list_and_length(taxonomy_string):
    tl = taxonomy_string.split(';')
    l = len(tl)
    return tl,l

def organize_taxonomy_info(taxonomy_dict):
    """Takes {seqID:taxonomy} and returns {seqID:(['D_1__'],[taxonomy_level])}"""
    nd = {}
    i = 0
    for seqID,taxonomy in taxonomy_dict.items():
        fixed_string = taxonomy.replace(';;',';')
        tl,l = get_list_and_length(fixed_string)
        nd[seqID] = (tl,l)
        if l > i:
            i = l
    # D means taxonomic depth 0 being root / top
    depth_list = ['D_' + str(n) + '__' for n in range(i)]
    
    td = {}
    for seqID,taxonomy_tup in nd.items():
        new_tax_list = taxonomy_tup[0] + ['']*(i-taxonomy_tup[1])
        c = zip(depth_list,new_tax_list)
        td[seqID] = c
    
    return td

def make_tax_string(taxonomy_tup_list):
    ttl = ''.join(taxonomy_tup_list)
    return ttl
        
def make_taxonomy_string(taxonomy_dict):
    fl = [seqID+'\t'+ ';'.join(map(make_tax_string,taxonomy_tup_list))\
          for seqID,taxonomy_tup_list in taxonomy_dict.items()]   
    fl_str = '\n'.join(fl)
    return fl_str

def main(infile_path,outfile_path):
    infile_handle = open(infile_path,'U')
    outfile_handle = open(outfile_path,'w')
    td = load_taxonomy_to_dict(infile_handle)
    to = organize_taxonomy_info(td)
    ts = make_taxonomy_string(to)
    infile_handle.close()
    outfile_handle.write(ts)
    outfile_handle.close()

if __name__ == '__main__':
    from sys import argv
    
    USE = "\nUse: python prep_silva_taxonomy_file.py infile outfile\n"
    
    if len(argv) != 3:
        print USE
    else:
        infile_path = argv[1]
        outfile_path = argv[2]
        main(infile_path,outfile_path)
    

