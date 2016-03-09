#!/usr/bin/env python
# file: prep_silva_data.py
# by Mike Robeson Feb 2013
# Parses a single FASTA database file from Silva and splits
# into two files: 1) fasta file with accession header and 2) a
# taxonomy file in the form of 'accession \t taxonomy'

from cogent.parse.fasta import MinimalFastaParser 
from string import maketrans

def parse_label(label):
    new_header,taxonomy = label.split(' ',1)
    return new_header,taxonomy

def parse_seq(seq):
    """convert T to U and remove whitespace"""
    trans_table = maketrans('U','T')
    dna_seq = seq.translate(trans_table,' ')
    return dna_seq

def process_silva(seqs, tax_out, seq_out):
    for label,seq in MinimalFastaParser(seqs):
        new_header,taxonomy = parse_label(label)
        fixed_seq = parse_seq(seq)
        tax_out.write(new_header + '\t' + taxonomy + '\n')
        seq_out.write('>' + new_header + '\n' + fixed_seq + '\n')

def main(seqs,tax_out,seq_out):
    process_silva(seqs, tax_out, seq_out)
    tax_out.close()
    seq_out.close()

if __name__ == '__main__':
    from sys import argv
    USE = "\nUSE: python prep_silva_data.py silva_fasta_infile taxonomy_outfile sequence_outfile\n"
    
    if len(argv) != 4:
        print USE
    else:
        seqs = open(argv[1])
        tax_out = open(argv[2], 'w')
        seq_out = open(argv[3], 'w')
        main(seqs, tax_out, seq_out)
    
