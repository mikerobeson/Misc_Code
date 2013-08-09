Tree_Processing
===============

This folder contains a collection of scripts that I use to help visualize and 
manipulate phylogenetic trees output from QIIME (http://qiime.org) and similar 
tools.

This code makes use of PyCogent (http://pycogent.org).

------------------------------
Using map_taxon_labels_to_tree.py and remove_taxonomy_from_tree.py:

I often make use of UniFrac (http://bmf.colorado.edu/unifrac/) to analyze my 
microbial community data. However, the majority of likelihood-based phylogenetic
tree building software does not output a rooted tree (required for UniFrac) 
by default. The above mentioned pair of scripts will append and remove the taxonomic
information to and from the tips of the given tree.

The reason for this, is to provide a quick way to visually inspect and properly
root trees for down stream UniFrac and QIIME analysis. For example, I use these
scripts to sanity-check my Bacteria phylogeny and root the tree to Archaea based 
on the taxonomy information added to the tips of the tree.

1) Use the script map_taxon_labels_to_tree.py to appended the taxonomic informaton to
   the tips of the tree using appropriate files generated via QIIME. A couple of these
   QIIME scripts are referred to below.

            python map_taxon_labels_to_tree.py  tree.infile  taxonomy.infile  tree.outfile  taxonomy.depth
            
            tree.infile     :    Newick formated tree.
                                 From 'make_phylogeny.py'.
            taxonomy.infile :    Taxonomy assignments from 'assign_taxonomy.py'.
            tree.outfile    :    Output location of your updated tree.
            taxonomy.depth  :    Number of taxonomy levels to retain starting at the root.
                                 If not set, will use a default value of 4.

2) View and root the tree based on the taxonomy labels added the tip of the tree
   from step 1. You can use a tree-viewer like Dendroscope
   (http://ab.inf.uni-tuebingen.de/software/dendroscope/) to do this. 
   Then save the tree file.

3) Now that the tree is properly rooted we need to trim off the very taxonomy labels 
   we added and used to guide our rooting. This is required if you wish to use the rooted
   tree in downstream QIIME analysis, as the tree tips should only ontain the OTU labels.

            python remove_taxonomy_from_tree.py  tree.infile  tree.outfile  regex.string
            
            tree.infile     :    Newick formated tree.
            tree.outfile    :    Output location of your updated tree.
            regex.string    :    String to remove. Default is '_k__.+'
                                 if not provided.

4) Now you have a properly rooted tree that is usable in QIIME.

------------------------------
