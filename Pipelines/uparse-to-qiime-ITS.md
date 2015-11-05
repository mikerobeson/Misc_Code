## UPARSE-to-QIIME for ITS and variable-length genes. ##

This is an update of a pipleine I had previously posted [here](https://groups.google.com/forum/#!msg/qiime-forum/zqmvpnZe26g/ksFmMwDHPi8J) with a focus on variable length genes like [ITS](https://en.wikipedia.org/wiki/Internal_transcribed_spacer) and [trnL](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1807943/), etc...

Depending on how your sequencing facility has processed your sequencing data some of the initial steps below may have to be altered. Some suggestions:

Look into:
   - QIIME's [multiple_join_paired_ends.py](http://qiime.org/scripts/multiple_join_paired_ends.html)
   - QIIME's [multiple_split_libraries_fastq.py](http://qiime.org/scripts/multiple_split_libraries_fastq.html)
   - If using Linux, I've found that using the [rename](http://www.computerhope.com/unix/rename.htm) command can be quite helpful for relabeling folders post `multiple_split_libraries_fastq.py` processing.
    

#### 1) OPTIONAL: trim primers ####
[cutadapt](https://github.com/marcelm/cutadapt) -g GTGCCAGCMGCCGCGGTAA -G GGACTACHVGGGTWTCTAAT -e 0.1 --discard-untrimmed --match-read-wildcards -o fw.reads.trimmed.fastq -p rev.reads.trimmed.fastq fw.reads.fastq rev.reads.fastq

*There are many primer trimming tools out there, but I think `cutadapt` is ideal. Notice, I use the detection of primers as a form of quality control. That is, I discard any sequence in which I cannot detect both the forward and reverse primers. However, if you are using [ITSx](http://microbiology.se/software/itsx/) you are probably better off leaving the primer sequences within the read for better ITS extraction.*

#### 2)  OPTIONAL: Merge paired ends. Skip if you just want to use the forward reads. ####
[join_paired_ends.py](http://qiime.org/scripts/join_paired_ends.html) -m fastq-join -b index.fastq -f fw.reads.trimmed.fastq -r rev.reads.trimmed.fastq -o merged_output/

*If you've an alternative tool to merge your paired ends but still need to sync your index (barcode) reads with your merged reads (i.e. many reads will fail to merge) then you can make use of my [remove_unused_barcodes.py](https://gist.github.com/mikerobeson/e5c0f0678a4785f8cf05) script. Keep in mind that the reads in both files should be in the same order, except for cases where the merged read for the corresponding index read is missing. If you are using `multiple_join_paired_ends.py` you can set options via the [parameters](http://qiime.org/documentation/qiime_parameters_files.html) file.*

#### 3) Split your libraries with quality filtering disabled or minimized. ####
[split_libraries_fastq.py](http://qiime.org/scripts/split_libraries_fastq.html) -q 0 --max_bad_run_length 250 --min_per_read_length_fraction 0.001 --store_demultiplexed_fastq -m mapping.txt --barcode_type golay_12 -b merged.barcodes.fastq --rev_comp_mapping_barcodes -i merged.fastq -o sl_out

*Remember, I decided to use the UPARSE quality filtering protocol instead of the one built-into `split_libraries_fastq.py`. For more info see [this](http://drive5.com/usearch/manual/avgq.html). This is why we use the `--store_demultiplexed_fastq` option. However, this quality filtering approach is optional, I sometimes use the the split libraries command above to do the quality filtering instead of UPARSE, it depends on the data. I initially mentioned some of these ideas [here](https://groups.google.com/d/msg/qiime-forum/zqmvpnZe26g/paTB6OSRiGwJ). If you are using `multiple_split_libraries.py` you can set many of these options via the [parameters](http://qiime.org/documentation/qiime_parameters_files.html) file. Whatever you end up doing, just make sure all your demultiplexed data is merged into one file. Use the [cat](https://en.wikipedia.org/wiki/Cat_(Unix)) command if needed. Eitherway you should have a final file called `seqs.fastq`*

#### 4) Get basic fastq stats to guide your quality filtering. ####
usearch7 -fastq_stats seqs.fastq -log seqs.stats.log.txt

#### 5) Quality filter. Optionally trim reads to fixed length if needed. ####
usearch7 -fastq_filter seqs.fastq -fastaout seqs.filt.fasta -fastqout seqs.filt.fastq -fastq_maxee 0.5 -fastq_trunclen 250

*This command just quality filters and trims the reads such that all reads are 250 bp in length (if you are going to use ITSx then there is probably no point to trimming to a fixed length at this point). `-fastq_trunclen` will "Truncate sequences at the L'th base. If the sequence is shorter than L, discard." I saved the fastq output just in case I need it. If you have all of the sequence between the primers and the read-lengths are not highly vairable like the ITS or trnL genes then you most likely do not need to trim post merging paired-ends. For more information about global trimming see [here](http://www.drive5.com/usearch/manual/global_trimming.html). WARNING: If you merged the ITS reads then they may be of variable length. In this case it is suggested that your [variable-length](http://www.drive5.com/usearch/manual/global_trimming_its.html) sequences be padded at the 3'-end with terminal Ns (up to your preferred sequence length) prior to quality filtering of the data. Not sure how much this really matters, especially if you are not trimming to a fixed length at this point, but just an FYI.*

#### 6) OPTIONAL: use ITSx to extract the ITS sequences. ####
- Option 1: Run ITSx Directly on ITS reads. Then, just to make this tutorial easier to follow rename the output.

    ITSx --cpu 2 --only_full T --save_regions all -t F -i seqs.filt.fasta -o ITSx.output
    
    mv ITSx.output seqs.filt.itsonly.fasta 


- Option 2:  Run my script to execute ITSx on multiple CPUs, then concatenate ITS gene output. Then, just to make this tutorial easier to follow, concatenate all the output from the parallel processing:

    [python parallel_itsx.py](https://gist.github.com/mikerobeson/e9b3e2ab05cb3b7a797a) -i seqs.filt.fasta -o ITSx.output 24 24000

    $ cat 'all-your-ITS2-fasta-ouput' > seqs.filt.itsonly.fastq


*This will take a while. Some colleagues of mine have warned me of potential over-clustering of different fungal taxa when not trimming the conserved rRNA ends of the resulting ITS data. I typically use [ITSx](http://microbiology.se/software/itsx/) when I do have the full ITS gene from merged paired-ends. Though you can fiddle with using this tool on only the forward reads. Mileage may vary. Keep in mind the comments of [Nguyen et al.](http://doi.org/10.1111/nph.12923) about losing taxonomic groups due to failed merges when using paired-end data. You can speed-up this step further by waiting until after  dereplicating the data. But this may cause problems at step 14 as you'll be trying to map your full filtered reads against the ITS-only reads.*

#### 7) Dereplicate reads and sort by read count. ####
usearch7 -derep_fulllength seqs.filt.itsonly.fasta -output seqs.filt.itsonly.derep.fasta -sizeout 


#### 8) Remove singletons ####
usearch7 -sortbysize seqs.filt.itsonly.derep.fasta -output seqs.filt.itsonly.derep.mc2.fasta -minsize 2

#### 9) Pick OTUs, perform *de novo* chimera checking. Optionally pad your sequences with Ns prios to OTU clustering.####
usearch7 -cluster_otus seqs.filt.itsonly.derep.mc2.fasta -otus seqs.filt.itsonly.derep.mc2.repset.fasta

*Note: despite what is said in [this](http://onlinelibrary.wiley.com/doi/10.1111/1462-2920.12610/abstract;jsessionid=2CD2390EEFFF1D570F2B94CAC3638AA7.f04t04) paper, it has always been possible to disable de novo chimera checking. All you need to do is add the flag `-uparse_break -999` to the above command. This effectively sets up the case for which "... chimeric models would never be optimal" See my initial post about this [here](https://groups.google.com/d/msg/qiime-forum/zqmvpnZe26g/V7hUUskPrqgJ). Also, for better clustering of highly variable reads like ITS you may want to pad your [variable-length](http://www.drive5.com/usearch/manual/global_trimming_its.html) sequences at the 3'-end with terminal Ns up to your preferred sequence length prior to OTU clustering. Remember usearch considers terminal gaps to be absolute differences!*

#### 10) OPTIONAL: If you padded your sequences then you need to remove Ns we added in step 9 prior to reference based chimera checking. ####
Lets pretend we did this and we end up with the following file:`seqs.filt.itsonly.derep.mc2.repset.notpadded.fasta`

*We must do this to obtain proper chimera detection and taxonomy assignment against reference databases. That is, they will not have those artificial Ns we added.*

#### 11) Perform reference-based chimera checking against UNITE database. Using non-padded sequences from Step 9. ####
usearch7 -uchime_ref seqs.filt.itsonly.derep.mc2.repset.notpadded.fasta -db ITSx.ref.db.otus -strand plus -minh 0.5 -nonchimeras seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.fasta -chimeras seqs.filt.itsonly.derep.mc2.repset.notpadded.chimeras.fasta -uchimealns seqs.filt.itsonly.derep.mc2.repset.notpadded.chimeraalns.txt -threads 24

*Note: Use the [UNITE](https://unite.ut.ee/repository.php) database for reference chimera detection and taxonomy aassignment for ITS. Also, make sure you check the `-uchimealns` output file. I've often had to adjust the `-minh` setting to something between 0.5 adn 1.5 as the default value of 0.28 can be to aggressive. In fact I've lost dominant OTUs in my data set becuase of this. In short, pick the appropriate reference database and cuttoff values appropriate for your data!*

#### 12) OPTIONAL: Filter padded fasta file with non-padded reference non-chimera fasta file. ####
filter_fasta.py -a seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.fasta -f  seqs.filt.itsonly.derep.mc2.repset.padded.fasta -o seqs.filt.itsonly.derep.mc2.repset.padded.nochimeras.fasta

*Only needed if you decided to keep things simple and you padded all of your data with Ns after step 6. We do this becuase we need to map the original processed reads back to OTUs (which would contain Ns) for the construction of our OTU table in the following steps . So we want to remove the chimeras from the N-padded file.*

#### 13) Continuing from step 11 (or 12), relabel your representative sequences with 'OTU' labels. ####
python fasta_number.py seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.fasta OTU_ > seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUs.fasta

*The UPARSE python scripts can be obtained from [here](http://drive5.com/python/).*

#### 14) Map the original quality filtered reads back to relabeled OTUs we just made####
usearch7 -usearch_global seqs.filt.itsonly.fasta -db seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUs.fasta -strand plus -id 0.97 -uc otu.map.uc -threads 24

*Note: I am using the non-N-padded data here. Change this command with the appropriate files.*

#### 15) Make tab-delim OTU table ####
python uc2otutab_mod.py otu.map.uc > seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.txt

*Note: I modified the function 'GetSampleID' in the script 'uc2otutab.py' from [here](http://drive5.com/python/) and renamed the script 'uc2otutab_mod.py'. The modified function is:*

    def GetSampleId(Label): 
       SampleID = Label.split()[0].split('_')[0] 
       return SampleID 

*I did this because my demultiplexed headers in the otu.map.uc looked like this:
"ENDO.O.2.KLNG.20.1_19 MISEQ03:119:000000000-A3N4Y:1:2101:28299:16762 1:N:0:GGTATGACTCA orig_bc=GGTATGACTCA new_bc=GGTATGACTCA bc_diffs=0" and all I need is the SampleID: "ENDO.O.2.KLNG.20.1". So I split on the underscore in `ENDO.O.2.KLNG.20.1_19`. Again, see [this](https://groups.google.com/d/msg/qiime-forum/zqmvpnZe26g/ksFmMwDHPi8J) post.*

#### 16) Convert to biom format. ####
[biom convert](http://biom-format.org/documentation/biom_conversion.html) --table-type="OTU table" --to-json -i sseqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.txt -o seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.biom

#### 17) Assign taxonomy using blast, uclust, or rdp. ####
[parallel_assign_taxonomy_blast.py](http://qiime.org/scripts/parallel_assign_taxonomy_blast.html) -v -O 4 -t ITSx.ref.db.tax -r ITSx.ref.db.otus -i seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUs.fasta -o blast_assigned_taxonomy

*Or use your favorite taxonomy assignment protocol within QIIME 1.9.1 or elsewhere. However, see [this](http://microbe.net/2015/02/24/issues-classifying-its-data-the-answer-could-be-simply-using-blast-during-taxonomy-assignment-in-qiime/) blog post about issues of ITS taxonomy assignment. Again, use the [UNITE](https://unite.ut.ee/repository.php) database.*

#### 18) Add taxonomy to biom table. ####
[biom add-metadata](http://biom-format.org/documentation/adding_metadata.html) -i seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.biom -o seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.blasttax.biom --observation-metadata-fp blast_assigned_taxonomy/seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUs_tax_assignments.txt --observation-header OTUID,taxonomy --sc-separated taxonomy

#### 19) OPTIONAL: go back and make another tab-delim (classic) version of the OTU table w/ taxonomy####
biom convert -i seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.blasttax.biom -o seqs.filt.itsonly.derep.mc2.repset.notpadded.nochimeras.OTUTable.blasttax.txt --to-tsv --header-key taxonomy --output-metadata-id ConsensusLineage

#### 20) Continue with your preferred post-processing and analysis.####
- Optional: Remove non-fungal sequences from OTU Table:
    - [filter_taxa_from_otu_table.py](http://qiime.org/scripts/filter_taxa_from_otu_table.html) -p k\__Fungi ...




