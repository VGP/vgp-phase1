# vgp-phase1
repository for materials to do with the VGP phase 1 data freeze, analyses,
and publication

### status:
- 2025-04-11 - Checking, verifying the assembly listings
- 2025-04-21 - finishing the complete RepeatMasking of all the assemblies

## definitions:
- ==primary== the best assembly (haplotype) for the species, to be used in the primary multiple-alignment
- ==seconday== the alternate haplotype that corresponds to the ==primary== assembly for this species.

## counting assemblies (total: 844 = 581 + 263)
1. primary: 581 == `cut -f16 VGPPhase1-freeze-1.0.tsv | grep -c GC`
2. primary with RefSeq version: 246 == `cut -f16,17 VGPPhase1-freeze-1.0.tsv | grep -c GCF`
3. secondary: 263 == `cut -f22 VGPPhase1-freeze-1.0.tsv | tr ',' '\n' | tr -d ' ' | grep GC | wc -l`

## GenBank vs. RefSeq assemblies

There are 246 primary assemblies that have both a GenBank and a RefSeq
released version from NCBI.  There are four files here to summarize
the differences between the two assemblies.  The differences are
always because one or the other assembly will have a ==chrMT== sequence
that is not in the other.

1. 47 identical assemblies, GenBank and RefSeq are identical in all sequences
2. 44 RefSeq assemblies have an added ==chrMT== sequence from the GenBank assembly
3. 124 RefSeq has removed the ==chrMT== sequence that was in the GenBank assembly
4. 31 assemblies have the same count of sequences, but each one has a unique ==chrMT== sequence
