# vgp-phase1
repository for materials to do with the VGP phase 1 data freeze, analyses,
and publication

# status: 2025-04-11 - Checking, verifying the assembly listings - Hiram

# counting assemblies
1. primary: 581 == `cut -f16 VGPPhase1-freeze-1.0.tsv | grep -c GC`
2. primary with RefSeq version: 247 == `cut -f16,17 VGPPhase1-freeze-1.0.tsv | grep -c GCF`
3. secondary: 261 == `cut -f22 VGPPhase1-freeze-1.0.tsv   | tr ',' '\n' | tr -d ' ' | grep GC | sort -u | wc -l`
