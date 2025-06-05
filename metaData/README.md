## the annotations file is a derivative

### From the spreadsheet **VGPPhase1-freeze-1.0.tsv** and
###    **UCSC.alignment.set.metaData.tsv**

With a selection of columns from those two files collected together
via the following command line steps:

`
printf "# accession\tLineage\tSuperorder\tOrders\tFamily\tOrders_English\tMYA\tScientificName\tEnglishName\tNCBI taxon ID\tAssemblyId\tasmId\tsciName\tUCSC_comName\tVGPLineage\n" > annotations.tsv

# one special case for GCA_009914755.4 (T2T-CHM13/hs1)

paste <(cut -f16,17 ../VGPPhase1-freeze-1.0.tsv|sed -e "s/\t$//g" -e "s/.*\t//"  | sed -e 's/GCF_009914755.1/GCA_009914755.4/;') \
   <(cut -f2-7,10-12,14 ../VGPPhase1-freeze-1.0.tsv) | grep GC | sort -k1 \
    | join -t$'\t' - \
      <(cut -f2-5,15 ../UCSC.alignment.set.metaData.tsv | sort -k1) \
         >> annotations.tsv
`

The UCSC browser shows the GCA_009914755.4 assembly rather than the
RefSeq GCF_009914755.1 assembly.  These are identical assemblies, with
the GenBank assembly GCA_009914755.4 having the additional mito sequence
**CP068254.1**
