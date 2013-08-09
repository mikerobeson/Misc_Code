#!/usr/bin/env python
# file: map_taxon_labels_to_tree.py
# by Mike Robeson 04-19-2013

#from cogent import LoadTree
from cogent.core.tree import PhyloNode
from cogent.parse.tree import DndParser

def parse_taxonomy(tfl):
    """ Returns dict of {otuID : taxonomy}
        tfl : taxon file handle
    """
    d = {}
    for line in tfl:
        otu,taxonomy = line.split('\t')[0:2]
        d[otu] = taxonomy
    return d

def shorten_taxonomy_strings(td, depth=4):
    """Returns a dictionary with shortened taxonomy labels
        example:
        D_0__Eukaryota;D_1__Fungi;D_2__Dikarya;D_3__Ascomycota;D_4__Pezizomycotina;D_5__Sordariomycetes;D_6__Hypocreomycetidae
        will return as:
        D_0__Eukaryota;D_1__Fungi;D_2__Dikarya;D_3__Ascomycota
    """
    std = {}
    for otuID,tax in td.items():
        tl = tax.split(';')
        taxonomy_depth_to_keep = tl[0:depth]
        new_str = '_'.join(taxonomy_depth_to_keep)
        std[otuID] = new_str
    return std


def assign_tax_labels_to_tree(tree,std):
    """Puts new tip labels onto tree
        tree : newick string
        std : output from shorten_taxonomy_strings
    """
    tree_nodes = DndParser(tree, PhyloNode)
    for node in tree_nodes.tips():
        label = node.Name
        tax = std[label]
        new_label = str(label) + '_' + tax
        node.Name = new_label 
    return tree_nodes

def main(intree, intax, outtree, depth):
    """main script workflow 
       intree : newick tree string
       intax : file handle to taxonomy file in the form of
               'otuID \t taxomony \t rdp support'
       outtree : output file handle
       depth : levels of taxonomy wanted starting at the root
    """
    tax = parse_taxonomy(intax)
    short_tax = shorten_taxonomy_strings(tax, depth)
    new_tree = assign_tax_labels_to_tree(intree, short_tax)
    new_tree.writeToFile(outtree)
    
    
if __name__ == '__main__':
    from sys import argv
    
    USAGE = """
            
            This script will append taxonomy information to the otuID tips of
            your phylogeny. This will make interpreting your tree in Dendroscope
            or FigTree much easier.
            
            USAGE:
            python map_taxon_labels_to_tree.py  tree.infile  taxonomy.infile  tree.outfile  taxonomy.depth
            
            tree.infile     :    Newick formated tree.
            taxonomy.infile :    Taxonomy assignments from 'assign_taxonomy.py'.
            tree.outfile    :    Output location of your updated tree.
            taxonomy.depth  :    Number of taxonomy levels to retain starting at the root.
                                 If not set, will use a default value of 4.
        """
    
    if len(argv) < 4:
        print USAGE
    elif len(argv) == 4:
        intree = open(argv[1],'U').read()
        intax = open(argv[2], 'U')
        outtree = argv[3] #open(argv[3], 'U')
        depth = 4
        main(intree, intax, outtree, depth)
        intax.close()
    else:
        intree = open(argv[1],'U').read()
        intax = open(argv[2], 'U')
        outtree = argv[3]
        depth = int(argv[4])
        main(intree, intax, outtree, depth)
        intax.close()
        

    
