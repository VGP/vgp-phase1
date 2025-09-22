## The masked sizes vs. assembly size graph does **not** include the non-vertebrate **out groups**.

## The **out groups** are:

| count | group | pri/sec |
| --: | :------: | :-------: |
| 1 | echinoderm | primary |
| 4 | invertebrate | primary |
| 11 | otherChordates| primary |
| 3 | invertebrate | secondary |
| 4 | otherChordates| secondary |
| 23 | total |

## The graph includes the following VGP groupings:

| count | group |
| --: | :------: |
| 32 | amphibians |
| 137 | birds |
| 159 | fish |
| 156 | mammals |
| 10 | primates |
| 55 | reptiles |
| 16 | sharks |
| 822 | total |


| count | group |
| --: | :------: |
| 565 | primary |
| 257 | secondary |
| 822 | total |

## The four files:

- primary.DFamMasking.tsv
- primary.modelerMasking.tsv
- secondary.DFamMasking.tsv
- secondary.modelerMasking.tsv

Show the listing of assemblies and the type of masking that was
applied to the download files from:
[UCSC alignment](https://hgdownload.soe.ucsc.edu/hubs/VGP/alignment/)

The RepeatModeler families were used when they applied more masking
to the assembly than was obtained from the DFam libraries from
RepeatMasker

## Repeat Modeler files:

Access to all Repeat Modeler files for repeats analysis can be found
via the following S3 resources:

- [primary assemblies](https://genomeark.s3.amazonaws.com/downstream_analyses/repeats/RepeatModeler/README.txt)
- [secondary assemblies](https://genomeark.s3.amazonaws.com/downstream_analyses/repeats/RepeatModeler/secondary/README.txt)
- [corrected large assemblies](https://genomeark.s3.amazonaws.com/downstream_analyses/repeats/RepeatModeler/over10G/README.over10G.txt)

To see the S3 files in the **corrected large assemblies**:

- GCA_026652325.1 - aws s3 ls s3://genomeark/downstream_analyses/repeats/RepeatModeler/over10Gb/GCA_026652325.1 --recursive
- GCA_040939525.1 - aws s3 ls s3://genomeark/downstream_analyses/repeats/RepeatModeler/over10Gb/GCA_040939525.1 --recursive
- GCA_964204655.1 - aws s3 ls s3://genomeark/downstream_analyses/repeats/RepeatModeler/over10Gb/GCA_964204655.1 --recursive
- GCA_964263255.1 - aws s3 ls s3://genomeark/downstream_analyses/repeats/RepeatModeler/over10Gb/GCA_964263255.1 --recursive
- GCF_040938575.1 - aws s3 ls s3://genomeark/downstream_analyses/repeats/RepeatModeler/over10Gb/GCF_040938575.1 --recursive

