#!/usr/bin/env python
# file: remove_taxonomy_from_tree.py
# by Mike Robeson 07-18-2013

#from cogent import LoadTree
from cogent.core.tree import PhyloNode
from cogent.parse.tree import DndParser
import re


def remove_taxonomy(tree, regex_string):
    """Puts new tip labels onto tree
        tree : LoadTree object
        regex_string : 
    """
    tree_nodes = DndParser(tree, PhyloNode)
    for node in tree_nodes.tips():
        label = node.Name
        p = re.compile(regex_string)
        new_label = p.sub('', label)
        #print new_label
        node.Name = new_label 
    return tree_nodes

def main(intree, outtree, regex_string='_k__.+'):
    """main script workflow 
       intree : LoadTree object
       regex_string : string to remove from tree tips
    """
    new_tree = remove_taxonomy(intree, regex_string)
    new_tree.writeToFile(outtree)
    
    
if __name__ == '__main__':
    from sys import argv
    
    USAGE = """
            
            This script will remove taxonomy information from the otu tips of
            placed onto your phylogeny from 'map_taxon_labels_to_tree.py'.
            
            In other words, you might have needed to root the tree to a specific
            group based on the taxonomy information. For further analysis you
            need to return the tree back a QIIME compatible format.  

            USAGE:
            python remove_taxonomy_from_tree.py  tree.infile  tree.outfile  regex.string
            
            tree.infile     :    Newick formated tree.
            tree.outfile    :    Output location of your updated tree.
            regex.string    :    String to remove. Default is '_k__.+'
                                 if not provided.
        """
    
    if len(argv) < 3:
        print USAGE
    elif len(argv) == 3:
        intree = open(argv[1],'U').read()
        outtree = argv[2] #open(argv[3], 'U')
        regex_string = '_k__.+'
        main(intree, outtree, regex_string)
    else:
        intree = open(argv[1],'U').read()
        outtree = argv[2]
        regex_string = str(argv[3])
        main(intree, outtree, regex_string)
        

    
