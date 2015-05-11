SILVA_to_RDP
============

Python code to parse SILVA fasta database files into usable form for the RDP classifier.


This collection of scripts will take a fasta formatted database file from the [SILVA
archive](http://www.arb-silva.de/download/archive/) and convert it into a form usable
by the RDP classifier. For example, I typically use these scripts to create my own LSU 
database for classifying Fungi via the [RDP classifier](http://rdp.cme.msu.edu) 
through [QIIME](http://qiime.org).

This code currently makes use of [PyCogent](http://pycogent.org) and will eventually 
be converted over to [scikit-bio](http://scikit-bio.org). 

This code was used, in part, to create the latest [Silva v119](http://www.arb-silva.de/no_cache/download/archive/qiime/)
reference database for [QIIME](http://qiime.org). I've updated the documentation here to 
reflect a more streamlined approach as suggested by [@walterst](https://gist.github.com/walterst). 
His notes are contained within [Silva_119_provisional_release.zip](http://www.arb-silva.de/fileadmin/silva_databases/qiime/Silva_119_provisional_release.zip).

The following procedures below should work identically.

## Procedure 1
1) Download either an ungapped or ungapped SILVA fasta file of choice from [here](http://www.arb-silva.de/download/archive/).
    
2) OPTIONAL : From [Primer Prospector](http://pprospector.sourceforge.net/index.html) run.
    [clean_fasta.py](http://pprospector.sourceforge.net/scripts/clean_fasta.html)
    This step is just to make sure the input files are sane for the following steps.

3) Generate a full taxonomy and raw fasta file from the raw sequence data.
    `python prep_silva_data.py <silva.fasta> <taxonomy.outfile.txt> <sequence.outfile.fasta>`

4) Remove any non-ASCII characters from the newly created taxonomy file using the script.
    [parse_nonstandard_chars.py](https://gist.github.com/walterst/0a4d36dbb20c54eeb952) from [@walterst](https://gist.github.com/walterst).
    These characters can cause the RDP classifier and other programs to fail.

5) Take the corrected taxonomy file and make it RDP friendly.
    `python prep_silva_taxonomy_file.py <taxonomy.outfile.txt> <taxonomy.rdp.outfile.txt>`
    As there can be many more than 7-levels of taxonomy (see below), you can change the 
    default parameters for `summarize_taxa` in your [qiime_config file](http://qiime.org/install/qiime_config.html). For example you 
    can add these lines to the qiime_config file: `summarize_taxa:level	2,3,4,5,6,7,8,9,10,11`. 
    This is beneficial when using [summarize_taxa_through_plots.py](http://qiime.org/scripts/summarize_taxa_through_plots.html)

6) Pick OTUs for 99%, 97%, 94%. Do this on the unaligned SILVA data. See this [thread](https://groups.google.com/d/msg/qiime-forum/KEvXuLwJB70/FK7h2e_gjjIJ) as 
    well as my [trick](https://groups.google.com/d/msg/qiime-forum/KEvXuLwJB70/LEaY4N9JXucJ) on how to quickly make 
    a representative sequence file based on the SILVA aligned fasta files.
    
7) From [QIIME](http://qiime.org) run [pick_rep_set.py](http://qiime.org/scripts/pick_rep_set.html) to make your OTU FASTA file.

8) Remove the OTU ID labels from the OTU FASTA (representative sequence) headers so that 
    they match the taxonomy file IDs from Step 3. Use the script [fix_fasta_labels.py](https://gist.github.com/walterst/f5c619799e6dc1f575a0) from [@walterst](https://gist.github.com/walterst) on your OTU FASTA file
    so that they match the actual representative sequence ID in the SILVA database (e.g. remove the OTU ID label).
    Now you can use the unaligned OTU FASTA files and the taxonomy file for [assign_taxonomy.py](http://qiime.org/scripts/assign_taxonomy.html)

9) OPTIONAL : If you want to force a 7-level taxonomy file you can make use of another
    script by [@walterst](https://gist.github.com/walterst): [parse_to_7_taxa_levels.py](https://gist.github.com/walterst/9ddb926fece4b7c0e12c)
    
10) OPTIONAL : Reduce the size of the SILVA alignment file as I recomend in this [post](https://groups.google.com/d/msg/qiime-forum/KEvXuLwJB70/LEaY4N9JXucJ). 
    Another approach was used by [@walterst](https://gist.github.com/walterst) in the above mentioned SILVA v119 
    notes file. That is, to create a [lane mask.](https://gist.github.com/walterst/db491ba0fd3916af6f5e), and feed to
    [filter_alignment.py](http://qiime.org/scripts/filter_alignment.html). Then use this as your reference alignment 
    for [align_seqs.py](http://qiime.org/scripts/align_seqs.html)



## Procedure 2 (summarized version of [@walterst's](https://gist.github.com/walterst) approach)
1) Download either an ungapped or ungapped SILVA fasta file of choice from [here](http://www.arb-silva.de/download/archive/).
    
2) From [Primer Prospector](http://pprospector.sourceforge.net/index.html) run
    [clean_fasta.py](http://pprospector.sourceforge.net/scripts/clean_fasta.html)
    This step is just to make sure the input files are sane for the following steps.
    
3) Pick OTUs for 99%, 97%, 94%. Do this for unaligned data. See this [thread](https://groups.google.com/d/msg/qiime-forum/KEvXuLwJB70/FK7h2e_gjjIJ) as 
    well as my [trick](https://groups.google.com/d/msg/qiime-forum/KEvXuLwJB70/LEaY4N9JXucJ) on how to quickly make 
    a representative sequence file based on the SILVA aligned fasta files.
    	
4) From [QIIME](http://qiime.org) run [pick_rep_set.py](http://qiime.org/scripts/pick_rep_set.html) to make your OTU FASTA file.
    
5) Use the script [fix_fasta_labels.py](https://gist.github.com/walterst/f5c619799e6dc1f575a0) from [@walterst](https://gist.github.com/walterst) on your OTU FASTA file
    so that they match the actual representative sequence ID in the SILVA database (e.g. remove the OTU ID label)

6) Generate a full taxonomy and raw fasta file from the unclustered raw sequence data. 
    Using this procedure we do not use the fasta file.
    `python prep_silva_data.py <silva.fasta> <taxonomy.outfile.txt> <sequence.outfile.fasta>`
    
7) Remove any non-ASCII characters from the newly created taxonomy file using the script
    [parse_nonstandard_chars.py](https://gist.github.com/walterst/0a4d36dbb20c54eeb952) from [@walterst](https://gist.github.com/walterst).
    These characters can cause the RDP classifier and other programs to fail.
    
8) Take the corrected taxonomy file and make it RDP friendly.
    `python prep_silva_taxonomy_file.py <taxonomy.outfile.txt> <taxonomy.rdp.outfile.txt>`
    As there can be many more than 7-levels of taxonomy (see below), you can change the 
    default parameters for `summarize_taxa` in your [qiime_config file](http://qiime.org/install/qiime_config.html). For example you 
    can add these lines to the qiime_config file:  
    `summarize_taxa:level	2,3,4,5,6,7,8,9,10,11`. 
    This is beneficial when using [summarize_taxa_through_plots.py](http://qiime.org/scripts/summarize_taxa_through_plots.html)

9) OPTIONAL : If you want to force a 7-level taxonomy file you can make use of another.
    script by [@walterst](https://gist.github.com/walterst): [parse_to_7_taxa_levels.py](https://gist.github.com/walterst/9ddb926fece4b7c0e12c)
    
10) OPTIONAL : Reduce the size of the SILVA alignment file as I recomend in this [post](https://groups.google.com/d/msg/qiime-forum/KEvXuLwJB70/LEaY4N9JXucJ). 
    Another approach was used by [@walterst](https://gist.github.com/walterst) in the above mentioned SILVA v119 
    notes file. That is, to create a [lane mask.](https://gist.github.com/walterst/db491ba0fd3916af6f5e)
    	 
11) I encourage that everyone read the great notes file from [@walterst](https://gist.github.com/walterst) within the 
    [Silva_119_provisional_release.zip](http://www.arb-silva.de/fileadmin/silva_databases/qiime/Silva_119_provisional_release.zip) 
    file. Especially, if you want to make your own database from SILVA (e.g. LSU).


```
    Otherwise If you just run:
    python prep_silva_data.py <silva.fasta> <taxonomy.outfile.txt> <sequence.outfile.fasta>
    python prep_silva_taxonomy_file.py <taxonomy.outfile.txt> <taxonomy.rdp.outfile.txt>

    You'll have two files that can be used to train your classifier or use for BLAST.
    RDP friendly taxonomy:                      <taxonomy.rdp.outfile.txt>
    FASTA file with only Accession headers:     <sequence.outfile.fasta>
    
    Obvuosly, keeping in mind any minor file edits as needed. See above Procedures.
```


