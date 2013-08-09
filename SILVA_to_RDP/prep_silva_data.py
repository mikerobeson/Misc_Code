#!/usr/bin/env python
# file: prep_silva_data.py
# by Mike Robeson Feb 2013
# Parses a single FASTA database file from Silva and splits
# into two files: 1) fasta file with accession header and 2) a
# taxonomy file in the form of 'accession \t taxonomy'

from cogent import LoadSeqs
from string import maketrans

def parse_label(label):
    new_header,taxonomy = label.split(' ',1)
    return new_header,taxonomy

def parse_seq(seq):
    """convert T to U and remove whitespace"""
    trans_table = maketrans('U','T')
    dna_seq = seq.translate(trans_table,' ')
    return dna_seq

def make_lists(seq_data):
    tax_list = []
    seq_list = []
    for label,seq in seq_data.items():
        new_header,taxonomy = parse_label(label)
        fixed_seq = parse_seq(seq)
        tax_list.append(new_header + '\t' + taxonomy)
        seq_list.append('>' + new_header + '\n' + fixed_seq)
    return tax_list, seq_list

def make_string(data_list):
    return '\n'.join(data_list)

def main(seq_data,tax_out,seq_out):
    tax_list,seq_list = make_lists(seq_data)
    tax_string = make_string(tax_list)
    seq_string = make_string(seq_list)
    tof = open(tax_out,'w')
    tof.write(tax_string)
    tof.close()
    sof = open(seq_out,'w')
    sof.write(seq_string)
    sof.close()

if __name__ == '__main__':
    from sys import argv
    USE = "\nUSE: python prep_silva_data.py silva_fasta_infile taxonomy_outfile sequence_outfile\n"
    
    if len(argv) != 4:
        print USE
    else:
        infile_path = LoadSeqs(argv[1],aligned=False)
        tax_out_path = argv[2]
        seq_out_path = argv[3]
        main(infile_path, tax_out_path, seq_out_path)
    
