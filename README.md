# vgp-phase1
repository for materials to do with the VGP phase 1 data freeze, analyses,
and publication

### status:
- 2025-05-10 - added taxId and taxon strings from NCBI for taxonomy analysis
            in two files: primary.taxon.metaData.tsv
            and secondary.taxon.metaData.tsv
- 2025-05-08 - replaced primary/otherChordates/GCF_010993605.1 with updated
            sea lamprey assembly: primary/otherChordates/GCA_048934315.1,
            moved GCF_010993605.1 to secondary,
            renamed GCF_009914755.1 to GCA_009914755.4 (T2T-CHM13v2.0)
- 2025-04-29 - assembly list verified, correctly repeat masked sequences
             now available at: [UCSC hgdownload](https://hgdownload.soe.ucsc.edu/hubs/VGP/alignment/)
- 2025-04-21 - finishing the complete RepeatMasking of all the assemblies
- 2025-04-11 - Checking, verifying the assembly listings

## definitions:
- **primary** the best assembly (haplotype) for the species, to be used in the primary multiple-alignment
- **seconday** the alternate haplotype that corresponds to the **primary** assembly for this species.

## counting assemblies (total: 845 = 581 + 264)
1. primary: 581 == `cut -f16 VGPPhase1-freeze-1.0.tsv | grep -c GC`
2. primary with RefSeq version: 246 == `cut -f16,17 VGPPhase1-freeze-1.0.tsv | grep -c GCF`
3. secondary: 264 == `cut -f22 VGPPhase1-freeze-1.0.tsv | tr ',' '\n' | tr -d ' ' | grep GC | wc -l`

## GenBank vs. RefSeq assemblies

There are 246 primary assemblies that have both a GenBank and a RefSeq
released version from NCBI.  There are four files here to summarize
the differences between the two assemblies.  The differences are
always because one or the other assembly will have a **chrMT** sequence
that is not in the other.

1. 47 identical assemblies, GenBank and RefSeq are identical in all sequences
2. 44 RefSeq assemblies have an added **chrMT** sequence from the GenBank assembly
3. 124 RefSeq has removed the **chrMT** sequence that was in the GenBank assembly
4. 31 assemblies have the same count of sequences, but each one has a unique **chrMT** sequence

## To Do List:
- common names need to be coordinated between UCSC names and the names
  from the spreadsheet.  We have a lot of different names right now,
  in general Erich's spreadsheet names will most likely prevail.
