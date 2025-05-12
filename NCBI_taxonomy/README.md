# Taxonomy derived from the NCBI 'Taxonomy common tree' web page.

### files here:
- newick tree, 581 species in plain text one line per scientific name
- same tree with taxon IDs in place of the scientific names
- same tree with the common names in place of the taxon IDs

### procedure:
- input the 581 different taxon IDs from this set of assemblies
- download the resulting phylip .phy tree from that page function
- convert to newick .nwk plain text format, one line per species
- the names returned from NCBI are the 'Scientific names' from NCBI taxonomy
- using a .sed file for conversion, convert those scientific names back to taxon IDs
- those taxon IDs can be converted to the assembly accession or to common names
