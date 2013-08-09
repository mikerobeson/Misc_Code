SILVA_to_RDP
============

Python code to parse SILVA fasta database files into usable form for the RDP classifier.


This collection of scripts will take a fasta formatted database file from the SILVA
archive (http://www.arb-silva.de/download/archive/) and convert it into a form usable
by the RDP classifier. For example, I typically use these scripts to create my own LSU 
database for classifying Fungi via the RDP classifier (http://rdp.cme.msu.edu) 
through QIIME (http://qiime.org).

This code makes use of PyCogent (http://pycogent.org).


USE:

    1) Download a SILVA fasta file.

    2) run:
        python prep_silva_data.py <silva.fasta> <taxonomy.outfile.txt> <sequence.outfile.fasta>

    3) then take the newly created taxonomy file and make it RDP friendly:
        python prep_silva_taxonomy_file.py <taxonomy.outfile.txt> <taxonomy.rdp.outfile.txt>

    Now you have two file that can be use to train your classifier or use for BLAST:
        RDP friendly taxonomy:                      <taxonomy.rdp.outfile.txt> 
        FASTA file with only Accession headers:     <sequence.outfile.fasta>


