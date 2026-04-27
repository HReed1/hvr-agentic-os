# Report 1: Module Inventory

## Fixed Modules
| Module | PR |
|--------|----|
| art/illumina | #7978 / #10378 |
| bcftools/call | #7978 / #10378 |
| bcftools/concat | #7978 / #10378 |
| bedgovcf | #7978 / #10378 |
| bowtie2/align | #7978 / #10378 |
| cat/fastq | #7978 / #10378 |
| delly/call | #7978 / #10378 |
| expansionhunter | #7978 / #10378 |
| gatk4/applyvqsr | #7978 / #10378 |
| gatk4/filtermutectcalls | #7978 / #10378 |
| gatk4/genotypegvcfs | #7978 / #10378 |
| gfastats | #7978 / #10378 |
| gfatools/gfa2fa | #7978 / #10378 |
| happy/happy | #7978 / #10378 |
| jasminesv | #7978 / #10378 |
| kmcp/search | #7978 / #10378 |
| lofreq/somatic | #7978 / #10378 |
| mosdepth | #7978 / #10378 |
| parabricks/mutectcaller | #7978 / #10378 |
| paragraph/vcf2paragraph | #7978 / #10378 |
| picard/liftovervcf | #7978 / #10378 |
| sentieon/gvcftyper | #7978 / #10378 |
| sentieon/haplotyper | #7978 / #10378 |
| seqkit/grep | #7978 / #10378 |
| shapeit5/switch | #7978 / #10378 |
| star/align | #7978 / #10378 |
| stranger | #7978 / #10378 |
| svdb/merge | #7978 / #10378 |
| vcflib/vcfbreakmulti | #7978 / #10378 |
| vt/normalize | #7978 / #10378 |

## Remaining Unfixed Modules
| Module | Stub Files | Scope |
|--------|------------|-------|
| abra2 | ${prefix}.abra.bam, ${prefix}.abra.bam | Proactive |
| artic/minion | ${prefix}.1.trimmed.rg.sorted.bam, ${prefix}.2.trimmed.rg.sorted.bam, ${prefix}.pass.vcf.gz, ${prefix}.primertrimmed.rg.sorted.bam, ${prefix}.primertrimmed.rg.sorted.bam, ${prefix}.sorted.bam, ${prefix}.sorted.bam, ${prefix}.trimmed.rg.sorted.bam, ${prefix}.trimmed.rg.sorted.bam | Proactive |
| bamaligncleaner | ${prefix}.bam | Proactive |
| bamclipper | ${prefix}.primerclipped.bam, ${prefix}.primerclipped.bam | Proactive |
| bamcmp | ${prefix}.bam, ${prefix2}.bam | Proactive |
| bamtools/split | ${prefix}.split1.bam, ${prefix}.unmapped.bam | Proactive |
| bamutil/clipoverlap | ${prefix}.bam | Proactive |
| bamutil/trimbam | ${prefix}.bam | Proactive |
| bbmap/align | ${prefix}.bam | Proactive |
| biobambam/bammarkduplicates2 | ${prefix}.bam | Proactive |
| biobambam/bammerge | ${prefix}.bam | Proactive |
| biscuit/align | ${prefix}.bam, ${prefix}.bam | Proactive |
| biscuit/biscuitblaster | ${prefix}.bam, ${prefix}.bam | Proactive |
| biscuit/bsconv | ${prefix}.bam | Proactive |
| bismark/align | ${prefix}.bam | Proactive |
| bismark/deduplicate | ${prefix}.deduplicated.bam | Proactive |
| bowtie/align | ${prefix}.bam | Proactive |
| bowtie2/align | ${prefix}.unmapped.fastq.gz, ${prefix}.unmapped_1.fastq.gz, ${prefix}.unmapped_2.fastq.gz | #5409 |
| bwa/sampe | ${prefix}.bam | Proactive |
| bwa/samse | ${prefix}.bam | Proactive |
| bwameth/align | ${prefix}.bam | Proactive |
| chromap/chromap | ${prefix}.bam | Proactive |
| circularmapper/realignsamfile | ${prefix}_realigned.bam | Proactive |
| coptr/map | ${prefix}.bam | Proactive |
| coptr/merge | ${prefix}.bam | Proactive |
| coverm/contig | ${prefix}.bam | Proactive |
| coverm/genome | ${prefix}.bam | Proactive |
| ctatsplicing/startocancerintrons | ${prefix}.cancer_intron_reads.sorted.bam, ${prefix}.cancer_intron_reads.sorted.bam, ${prefix}.gene_reads.sorted.sifted.bam, ${prefix}.gene_reads.sorted.sifted.bam | Proactive |
| dedup | ${prefix}.bam | Proactive |
| deeptools/alignmentsieve | ${prefix}_as.bam | Proactive |
| disambiguate | ${prefix}.disambiguatedSpeciesA.bam, ${prefix}.disambiguatedSpeciesB.bam, ${prefix}.ambiguousSpeciesA.bam, ${prefix}.ambiguousSpeciesB.bam | Proactive |
| expansionhunter | ${prefix}_realigned.bam | Proactive |
| fgbio/copyumifromreadname | ${prefix}.bam | Proactive |
| fibertoolsrs/addnucleosomes | ${prefix}.bam | Proactive |
| fibertoolsrs/predictm6a | ${prefix}.bam | Proactive |
| gatk4/fastqtosam | ${prefix}.bam | Proactive |
| gatk4/haplotypecaller | ${prefix}.vcf.gz, ${prefix}.vcf.gz | #5409 |
| gatk4/markduplicates | ${prefix_no_suffix}.bam, ${prefix_no_suffix}.cram, ${prefix_no_suffix}.cram | Proactive |
| gatk4/mergebamalignment | ${prefix}.bam | Proactive |
| gatk4/revertsam | ${prefix}.reverted.bam | Proactive |
| gatk4/splitncigarreads | ${prefix}.bam | Proactive |
| gatk4/unmarkduplicates | ${prefix}.bam | Proactive |
| gem3/gem3mapper | ${prefix}.bam | Proactive |
| hisat2/align | ${prefix}.bam | Proactive |
| hlala/typing | results/extraction.bam, results/extraction.bam, results/extraction_mapped.bam, results/extraction_unmapped.bam, results/remapped_with_a.bam, results/remapped_with_a.bam | Proactive |
| isoseq/cluster | ${prefix}.transcripts.bam, ${prefix}.transcripts.bam | Proactive |
| isoseq/refine | ${prefix}.bam, ${prefix}.bam | Proactive |
| isoseq3/tag | ${prefix}.flt.bam, ${prefix}.flt.bam | Proactive |
| ivar/trim | ${prefix}.bam | Proactive |
| leehom | ${prefix}.bam | Proactive |
| leviosam2/lift | ${prefix}.bam | Proactive |
| lofreq/alnqual | ${prefix}.bam | Proactive |
| lofreq/indelqual | ${prefix}.bam | Proactive |
| lofreq/viterbi | ${prefix}.bam | Proactive |
| metamdbg/asm | ${prefix}.contigs.fasta.gz | #5409 |
| modkit/callmods | ${prefix}.bam | Proactive |
| modkit/repair | ${prefix}.bam | Proactive |
| mudskipper/bulk | ${prefix}.bam | Proactive |
| nextgenmap | ${prefix}.bam | Proactive |
| parabricks/applybqsr | ${prefix}.bam, ${prefix}.bam | Proactive |
| paraphase | ${prefix}.paraphase.bam, ${prefix}.paraphase.bam, ${prefix}_paraphase_vcfs/${prefix}_stub.vcf.gz | Proactive |
| pbbam/pbmerge | ${prefix}.bam, ${prefix}.bam | Proactive |
| pbccs | ${prefix}.chunk1.bam, ${prefix}.chunk1.bam | Proactive |
| pbjasmine | ${prefix}.bam | Proactive |
| pbmm2/align | ${prefix}.bam | Proactive |
| pbtk/pbmerge | ${prefix}.bam, ${prefix}.bam | Proactive |
| pharmcat/vcfpreprocessor | ${prefix}.preprocessed.vcf.bgz | Proactive |
| pharokka/installdatabases | $prefix/VFDB_setB_pro.fas.gz | #5409 |
| picard/fastqtosam | ${prefix}.bam | Proactive |
| picard/mergesamfiles | ${prefix}.bam | Proactive |
| picard/positionbaseddownsamplesam | ${prefix}.ds10.bam, ${prefix}.ds10.bam | Proactive |
| picard/setnmmdanduqtags | ${prefix}.bam | Proactive |
| pmdtools/filter | ${prefix}.bam | Proactive |
| popscle/freemuxlet | ${prefix}.clust1.samples.gz, ${prefix}.clust1.vcf.gz, ${prefix}.clust0.samples.gz, ${prefix}.clust0.vcf.gz | #5409 |
| portello | ${prefix}.vcf.gz, ${prefix}_unassembled.bam, ${prefix}_remapped.bam | Proactive |
| rastair/methylkit | ${prefix}.methylkit.txt.gz | #5409 |
| rsem/calculateexpression | ${prefix}.STAR.genome.bam, ${prefix}.genome.bam, ${prefix}.transcript.bam | Proactive |
| rseqc/splitbam | ${prefix}.in.bam, ${prefix}.ex.bam, ${prefix}.junk.bam | Proactive |
| samtools/ampliconclip | ${prefix}.cliprejects.bam | Proactive |
| samtools/calmd | ${prefix}.bam | Proactive |
| samtools/import | ${prefix}.bam | Proactive |
| samtools/reheader | ${prefix}.bam | Proactive |
| sawfish/discover | ${prefix}/contig.alignment.bam, ${prefix}/contig.alignment.bam | Proactive |
| sawfish/jointcall | ${prefix}/${prefix}_genotyped.sv.vcf.gz, ${prefix}/contig.alignment.bam, ${prefix}/contig.alignment.bam | Proactive |
| sentieon/rsemcalculateexpression | ${prefix}.STAR.genome.bam, ${prefix}.genome.bam, ${prefix}.transcript.bam | Proactive |
| sentieon/staralign | ${prefix}Xd.out.bam, ${prefix}.sortedByCoord.out.bam, ${prefix}.toTranscriptome.out.bam, ${prefix}.Aligned.unsort.out.bam, ${prefix}.Aligned.sortedByCoord.out.bam | Proactive |
| slamdunk/all | outputs/map/${prefix}.bam, outputs/filter/${prefix}_filtered.bam, outputs/filter/${prefix}_filtered.bam | Proactive |
| snapaligner/align | test.bam, test.bam | Proactive |
| snippy/run | ${prefix}/${prefix}.bam, ${prefix}/${prefix}.bam, ${prefix}/${prefix}.vcf.gz | Proactive |
| star/align | ${prefix}Xd.out.bam, ${prefix}.sortedByCoord.out.bam, ${prefix}.toTranscriptome.out.bam, ${prefix}.Aligned.unsort.out.bam, ${prefix}.Aligned.sortedByCoord.out.bam | Proactive |
| staramr/search | ${prefix}_results/{summary,detailed_summary,resfinder,pointfinder,plasmidfinder,mlst}.tsv.gz, ${prefix}_results/settings.txt.gz | #5409 |
| svtyper/svtyper | ${prefix}.bam | Proactive |
| tagbam | ${prefix}.bam | Proactive |
| telescope/assign | ${prefix}-updated.bam, ${prefix}-other.bam | Proactive |
| trgt/genotype | ${prefix}.spanning.bam | Proactive |
| ultra/align | ${prefix}.bam | Proactive |
| umitools/dedup | ${prefix}.bam | Proactive |
| umitools/prepareforrsem | ${meta.id}.bam | Proactive |
| variantbam | ${prefix}.bam | Proactive |
| vt/decomposeblocksub | ${prefix}.vcf.gz | #5409 |
| whatshap/haplotag | ${prefix}.bam | Proactive |
| yara/mapper | ${prefix}.mapped.bam, ${prefix}.mapped.bam, ${prefix}_1.mapped.bam, ${prefix}_2.mapped.bam | Proactive |

## Fix Pattern
```bash
echo '' | gzip > filename.gz
```