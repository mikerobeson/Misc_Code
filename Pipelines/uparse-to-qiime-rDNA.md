## UPARSE-to-QIIME for rDNA ##

This is an update of a pipleine I had previously posted [here](https://groups.google.com/forum/#!msg/qiime-forum/zqmvpnZe26g/ksFmMwDHPi8J)

Depending on how your sequencing facility has processed your sequencing data some of the initial steps below may have to be altered. Some suggestions:

Look into:
   - QIIME's [multiple_join_paired_ends.py](http://qiime.org/scripts/multiple_join_paired_ends.html)
   - QIIME's [multiple_split_libraries_fastq.py](http://qiime.org/scripts/multiple_split_libraries_fastq.html)
   - If using Linux, I've found that using the [rename](http://www.computerhope.com/unix/rename.htm) command can be quite helpful for relabeling folders post `multiple_split_libraries_fastq.py` processing.
    

#### 1) Merge paired ends. ####
[join_paired_ends.py](http://qiime.org/scripts/join_paired_ends.html) -m fastq-join -b index.fastq -f R1.reads.fastq -r R2.reads.fastq -o merged_output/

*If you've an alternative tool to merge your paired ends but still need to sync your index (barcode) reads with your merged reads (i.e. many reads will fail to merge) then you can make use of my [remove_unused_barcodes.py](https://gist.github.com/mikerobeson/e5c0f0678a4785f8cf05) script. Keep in mind that the reads in both files should be in the same order, except for cases where the merged read for the corresponding index read is missing. If you are using `multiple_join_paired_ends.py` you can set options via the [parameters](http://qiime.org/documentation/qiime_parameters_files.html) filei.*

#### 2) Split your libraries with quality filtering disabled or minimized. ####
[split_libraries_fastq.py](http://qiime.org/scripts/split_libraries_fastq.html) -q 0 --max_bad_run_length 250 --min_per_read_length_fraction 0.001 --store_demultiplexed_fastq -m miseq2_mapping.txt --barcode_type golay_12 -b merged.barcodes.fastq --rev_comp_mapping_barcodes -i merged.fastq -o sl_out

*Remember, I decided to use the UPARSE quality filtering protocol instead of the one built-into `split_libraries_fastq.py`. For more info see [this](http://drive5.com/usearch/manual/avgq.html). This is why we use the `--store_demultiplexed_fastq` option. However, this quality filtering approach is optional, I sometimes use the the split libraries command above to do the quality filtering instead of UPARSE, it depends on the data. I initially mentioned some of these ideas [here](https://groups.google.com/d/msg/qiime-forum/zqmvpnZe26g/paTB6OSRiGwJ). If you are using `multiple_split_libraries.py` you can set many of these options via the [parameters](http://qiime.org/documentation/qiime_parameters_files.html) file. Whatever you end up doing, just make sure all your demultiplexed data is merged into one file. Use the [cat](https://en.wikipedia.org/wiki/Cat_(Unix)) command if needed. Eitherway you should have a final file called `seqs.fastq`*

#### 3) Trim primers - if you have them. ####
[cutadapt](https://github.com/marcelm/cutadapt) -g GTGYCAGCMGCCGCGGTA -a ATTAGAWACCCBDGTAGTCC -n 2 -e 0.1 --discard-untrimmed --match-read-wildcards seqs.fastq -o seqs.prtrim.fastq 

*There are many primer trimming tools out there, but I think `cutadapt` is ideal. Notice, I use the detection of primers as a form of quality control. That is, I discard any sequence in which I cannot detect both the forward and reverse primers.*

#### 4) Get basic fastq stats to guide your quality filtering. ####
usearch7 -fastq_stats seqs.prtrim.fastq -log seqs.prtrim.stats.log.txt

#### 5) Quality filter; trim reads to fixed length (if needed). ####
usearch7 -fastq_filter seqs.prtrim.fastq -fastaout seqs.prtrim.filt.fasta -fastqout seqs.prtrim.filt.fastq -fastq_maxee 0.5 -fastq_trunclen 250

*This command jsut quality filters and trims the reads such that all reads are 250 bp in length. `-fastq_trunclen` will "Truncate sequences at the L'th base. If the sequence is shorter than L, discard. I saved the fastq output just in case I need it.*

#### 6) Dereplicate reads and sort by read count. ####
usearch7 -derep_fulllength seqs.prtrim.filt.fasta -output seqs.prtrim.filt.derep.fasta -sizeout 

#### 7) Remove singletons ####
usearch7 -sortbysize seqs.prtrim.filt.derep.fasta -output seqs.prtrim.filt.derep.mc2.fasta -minsize 2

#### 8) Pick OTUs, perform *de novo* chimera checking. ####
usearch7 -cluster_otus seqs.prtrim.filt.derep.mc2.fasta -otus seqs.prtrim.filt.derep.mc2.repset.fasta

*Note: despite what is said in [this](http://onlinelibrary.wiley.com/doi/10.1111/1462-2920.12610/abstract;jsessionid=2CD2390EEFFF1D570F2B94CAC3638AA7.f04t04) paper, it has always been possible to disable de novo chimera checking. All you need to do is add the flag `-uparse_break -999` to the above command. This effectively sets up the case for which "... chimeric models would never be optimal" See my initial post about this [here](https://groups.google.com/d/msg/qiime-forum/zqmvpnZe26g/V7hUUskPrqgJ).*

#### 9) Perform reference-based chimera checking. ####
usearch7 -uchime_ref seqs.prtrim.filt.derep.mc2.repset.fasta -db greengenes.otus.97 -strand plus -minh 0.5 -nonchimeras seqs.prtrim.filt.derep.mc2.repset.nochimeras.fasta -chimeras seqs.prtrim.filt.derep.mc2.repset.chimeras.fasta -uchimealns seqs.prtrim.filt.derep.mc2.repset.chimeraalns.txt -threads 24

*Note: although the [Gold database](http://drive5.com/uchime/uchime_download.html) is [preferred](http://drive5.com/usearch/manual/uparse_pipeline.html) by Robert Edgar. I have had more stable and better results using the new GreenGenes or SILVA databases. Also, make sure you check the `-uchimealns` output file. I've often had to adjust the `-minh` setting to something between 0.5 adn 1.5 as the default value of 0.28 can be to aggressive. In fact I've lost dominant OTUs in my data set becuase of this. In short, pick the appropriate reference database and cuttoff values appropriate for your data!*

#### 10) Relabel your representativ sequences with 'OTU' labels. ####
python fasta_number.py seqs.prtrim.filt.derep.mc2.repset.nochimeras.fasta OTU_ > seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUs.fasta

*This and other UPARSE python scripts can be obtained from [here](http://drive5.com/python/).*

#### 11) Map the original quality filtered reads back to relabeled OTUs we just made####
usearch7 -usearch_global seqs.prtrim.filt.fasta -db seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUs.fasta -strand plus -id 0.97 -uc otu.map.uc -threads 24

#### 12) Make tab-delim OTU table ####
python uc2otutab_mod.py otu.map.uc > seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.txt

*Note: I modified the function 'GetSampleID' in the script 'uc2otutab.py' from [here](http://drive5.com/python/) and renamed the script 'uc2otutab_mod.py'. The modified function is:*

    def GetSampleId(Label): 
       SampleID = Label.split()[0].split('_')[0] 
       return SampleID 

*I did this because my demultiplexed headers in the otu.map.uc looked like this:
"ENDO.O.2.KLNG.20.1_19 MISEQ03:119:000000000-A3N4Y:1:2101:28299:16762 1:N:0:GGTATGACTCA orig_bc=GGTATGACTCA new_bc=GGTATGACTCA bc_diffs=0" and all I need is the SampleID: "ENDO.O.2.KLNG.20.1". So I split on the underscore in `ENDO.O.2.KLNG.20.1_19`. Again, see [this](https://groups.google.com/d/msg/qiime-forum/zqmvpnZe26g/ksFmMwDHPi8J) post.*

#### 13) Convert to biom format. ####
[biom convert](http://biom-format.org/documentation/biom_conversion.html) --table-type="OTU table" --to-json -i seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.txt -o seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.biom

#### 14) Assign taxonomy. ####
[parallel_assign_taxonomy_rdp.py](http://qiime.org/scripts/parallel_assign_taxonomy_rdp.html) -v --rdp_max_memory 3000 -O 4 -t greengenes.otus.97.tax -r greengenes.otus.97 -i seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUs.fasta -o rdp_gg97_assigned_taxonomy

*Or use your favorite taxonomy assignment protocol within QIIME 1.9.1 or elsewhere.*

#### 15) Add taxonomy to biom table. ####
[biom add-metadata](http://biom-format.org/documentation/adding_metadata.html) -i seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.biom -o seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.rdpggtax.biom --observation-metadata-fp rdp_gg97_assigned_taxonomy/seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUs_tax_assignments.txt --observation-header OTUID,taxonomy --sc-separated taxonomy

#### 16) make a tab-delim (classic) version of the OTU table####
biom convert -i seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.rdpggtax.biom -o seqs.prtrim.filt.derep.mc2.repset.nochimeras.OTUTable.rdpggtax.txt --to-tsv --header-key taxonomy

#### 17) Continue with your preferred post-processing and analysis.####
- Remove plastid sequences the data:
    - [filter_taxa_from_otu_table.py](http://qiime.org/scripts/filter_taxa_from_otu_table.html) -n  c\__Chloroplast,f\__mitochondria ...
- Align reads with PyNAST adn remove alignment failures from OTU table:
    - [parallel_align_seqs_pynast.py](http://qiime.org/scripts/parallel_align_seqs_pynast.html) ...
    - [filter_otus_from_otu_table.py](http://qiime.org/scripts/filter_otus_from_otu_table.html) -e alignment.failures ...
