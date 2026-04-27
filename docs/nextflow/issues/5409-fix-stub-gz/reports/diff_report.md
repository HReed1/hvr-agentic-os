# Report 2: Diff Report

| Module | Confidence | Conditional Logic | Scope |
|--------|------------|-------------------|-------|
| abra2 | MEDIUM | True | Proactive |
| artic/minion | MEDIUM | True | Proactive |
| bamaligncleaner | MEDIUM | True | Proactive |
| bamclipper | MEDIUM | True | Proactive |
| bamcmp | MEDIUM | True | Proactive |
| bamtools/split | MEDIUM | True | Proactive |
| bamutil/clipoverlap | MEDIUM | True | Proactive |
| bamutil/trimbam | MEDIUM | True | Proactive |
| bbmap/align | MEDIUM | True | Proactive |
| biobambam/bammarkduplicates2 | MEDIUM | True | Proactive |
| biobambam/bammerge | MEDIUM | True | Proactive |
| biscuit/align | MEDIUM | True | Proactive |
| biscuit/biscuitblaster | MEDIUM | True | Proactive |
| biscuit/bsconv | MEDIUM | True | Proactive |
| bismark/align | MEDIUM | True | Proactive |
| bismark/deduplicate | MEDIUM | True | Proactive |
| bowtie/align | MEDIUM | True | Proactive |
| bowtie2/align | MEDIUM | True | #5409 |
| bwa/sampe | MEDIUM | True | Proactive |
| bwa/samse | MEDIUM | True | Proactive |
| bwameth/align | MEDIUM | True | Proactive |
| chromap/chromap | MEDIUM | True | Proactive |
| circularmapper/realignsamfile | MEDIUM | True | Proactive |
| coptr/map | MEDIUM | True | Proactive |
| coptr/merge | MEDIUM | True | Proactive |
| coverm/contig | MEDIUM | True | Proactive |
| coverm/genome | MEDIUM | True | Proactive |
| ctatsplicing/startocancerintrons | MEDIUM | True | Proactive |
| dedup | MEDIUM | True | Proactive |
| deeptools/alignmentsieve | MEDIUM | True | Proactive |
| disambiguate | MEDIUM | True | Proactive |
| expansionhunter | MEDIUM | True | Proactive |
| fgbio/copyumifromreadname | MEDIUM | True | Proactive |
| fibertoolsrs/addnucleosomes | MEDIUM | True | Proactive |
| fibertoolsrs/predictm6a | MEDIUM | True | Proactive |
| gatk4/fastqtosam | MEDIUM | True | Proactive |
| gatk4/haplotypecaller | MEDIUM | True | #5409 |
| gatk4/markduplicates | MEDIUM | True | Proactive |
| gatk4/mergebamalignment | MEDIUM | True | Proactive |
| gatk4/revertsam | MEDIUM | True | Proactive |
| gatk4/splitncigarreads | MEDIUM | True | Proactive |
| gatk4/unmarkduplicates | MEDIUM | True | Proactive |
| gem3/gem3mapper | MEDIUM | True | Proactive |
| hisat2/align | MEDIUM | True | Proactive |
| hlala/typing | HIGH | False | Proactive |
| isoseq/cluster | MEDIUM | True | Proactive |
| isoseq/refine | MEDIUM | True | Proactive |
| isoseq3/tag | MEDIUM | True | Proactive |
| ivar/trim | MEDIUM | True | Proactive |
| leehom | MEDIUM | True | Proactive |
| leviosam2/lift | MEDIUM | True | Proactive |
| lofreq/alnqual | MEDIUM | True | Proactive |
| lofreq/indelqual | MEDIUM | True | Proactive |
| lofreq/viterbi | MEDIUM | True | Proactive |
| metamdbg/asm | MEDIUM | True | #5409 |
| modkit/callmods | MEDIUM | True | Proactive |
| modkit/repair | MEDIUM | True | Proactive |
| mudskipper/bulk | MEDIUM | True | Proactive |
| nextgenmap | MEDIUM | True | Proactive |
| parabricks/applybqsr | MEDIUM | True | Proactive |
| paraphase | MEDIUM | True | Proactive |
| pbbam/pbmerge | MEDIUM | True | Proactive |
| pbccs | MEDIUM | True | Proactive |
| pbjasmine | MEDIUM | True | Proactive |
| pbmm2/align | MEDIUM | True | Proactive |
| pbtk/pbmerge | MEDIUM | True | Proactive |
| pharmcat/vcfpreprocessor | MEDIUM | True | Proactive |
| pharokka/installdatabases | MEDIUM | True | #5409 |
| picard/fastqtosam | MEDIUM | True | Proactive |
| picard/mergesamfiles | MEDIUM | True | Proactive |
| picard/positionbaseddownsamplesam | MEDIUM | True | Proactive |
| picard/setnmmdanduqtags | MEDIUM | True | Proactive |
| pmdtools/filter | MEDIUM | True | Proactive |
| popscle/freemuxlet | MEDIUM | True | #5409 |
| portello | MEDIUM | True | Proactive |
| rastair/methylkit | MEDIUM | True | #5409 |
| rsem/calculateexpression | MEDIUM | True | Proactive |
| rseqc/splitbam | MEDIUM | True | Proactive |
| samtools/ampliconclip | MEDIUM | True | Proactive |
| samtools/calmd | MEDIUM | True | Proactive |
| samtools/import | MEDIUM | True | Proactive |
| samtools/reheader | MEDIUM | True | Proactive |
| sawfish/discover | MEDIUM | True | Proactive |
| sawfish/jointcall | MEDIUM | True | Proactive |
| sentieon/rsemcalculateexpression | MEDIUM | True | Proactive |
| sentieon/staralign | MEDIUM | True | Proactive |
| slamdunk/all | MEDIUM | True | Proactive |
| snapaligner/align | HIGH | False | Proactive |
| snippy/run | MEDIUM | True | Proactive |
| star/align | MEDIUM | True | Proactive |
| staramr/search | MEDIUM | True | #5409 |
| svtyper/svtyper | MEDIUM | True | Proactive |
| tagbam | MEDIUM | True | Proactive |
| telescope/assign | MEDIUM | True | Proactive |
| trgt/genotype | MEDIUM | True | Proactive |
| ultra/align | MEDIUM | True | Proactive |
| umitools/dedup | MEDIUM | True | Proactive |
| umitools/prepareforrsem | HIGH | False | Proactive |
| variantbam | MEDIUM | True | Proactive |
| vt/decomposeblocksub | MEDIUM | True | #5409 |
| whatshap/haplotag | MEDIUM | True | Proactive |
| yara/mapper | MEDIUM | True | Proactive |

## Diffs

### abra2
```diff
--- a/modules/nf-core/abra2/main.nf
+++ b/modules/nf-core/abra2/main.nf
@@ -48,8 +48,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.abra.bam
-    touch ${prefix}.abra.bam.bai
+    echo '' | gzip > ${prefix}.abra.bam
+    echo '' | gzip > ${prefix}.abra.bam.bai
     """
 }
```

### artic/minion
```diff
--- a/modules/nf-core/artic/minion/main.nf
+++ b/modules/nf-core/artic/minion/main.nf
@@ -54,10 +54,10 @@
     stub:
     prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.1.trimmed.rg.sorted.bam
+    echo '' | gzip > ${prefix}.1.trimmed.rg.sorted.bam
     touch ${prefix}.1.trimmed.rg.sorted.bai
     touch ${prefix}.1.vcf
-    touch ${prefix}.2.trimmed.rg.sorted.bam
+    echo '' | gzip > ${prefix}.2.trimmed.rg.sorted.bam
     touch ${prefix}.2.trimmed.rg.sorted.bai
     touch ${prefix}.2.vcf
 
@@ -82,20 +82,20 @@
 
     touch ${prefix}.pass.vcf
     echo "" | gzip > ${prefix}.pass.vcf.gz
-    touch ${prefix}.pass.vcf.gz.tbi
+    echo '' | gzip > ${prefix}.pass.vcf.gz.tbi
 
     touch ${prefix}.preconsensus.fasta
     touch ${prefix}.preconsensus.fasta.fai
 
     touch ${prefix}.primers.vcf
     touch ${prefix}.primersitereport.txt
-    touch ${prefix}.primertrimmed.rg.sorted.bam
-    touch ${prefix}.primertrimmed.rg.sorted.bam.bai
+    echo '' | gzip > ${prefix}.primertrimmed.rg.sorted.bam
+    echo '' | gzip > ${prefix}.primertrimmed.rg.sorted.bam.bai
 
-    touch ${prefix}.sorted.bam
-    touch ${prefix}.sorted.bam.bai
-    touch ${prefix}.trimmed.rg.sorted.bam
-    touch ${prefix}.trimmed.rg.sorted.bam.bai
+    echo '' | gzip > ${prefix}.sorted.bam
+    echo '' | gzip > ${prefix}.sorted.bam.bai
+    echo '' | gzip > ${prefix}.trimmed.rg.sorted.bam
+    echo '' | gzip > ${prefix}.trimmed.rg.sorted.bam.bai
     """
 }
```

### bamaligncleaner
```diff
--- a/modules/nf-core/bamaligncleaner/main.nf
+++ b/modules/nf-core/bamaligncleaner/main.nf
@@ -32,7 +32,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
 
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### bamclipper
```diff
--- a/modules/nf-core/bamclipper/main.nf
+++ b/modules/nf-core/bamclipper/main.nf
@@ -33,8 +33,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.primerclipped.bam
-    touch ${prefix}.primerclipped.bam.bai
+    echo '' | gzip > ${prefix}.primerclipped.bam
+    echo '' | gzip > ${prefix}.primerclipped.bam.bai
     """
 }
```

### bamcmp
```diff
--- a/modules/nf-core/bamcmp/main.nf
+++ b/modules/nf-core/bamcmp/main.nf
@@ -63,8 +63,8 @@
     if ("${prefix}.bam"    == "${prefix2}.bam" )
         error "Output names for the two bam files are identical, use \"task.ext.prefix\" and \"task.ext.prefix2\" to disambiguate!"
     """
-    touch ${prefix}.bam
-    touch ${prefix2}.bam
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix2}.bam
     """
 
 }
```

### bamtools/split
```diff
--- a/modules/nf-core/bamtools/split/main.nf
+++ b/modules/nf-core/bamtools/split/main.nf
@@ -34,8 +34,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.split1.bam
-    touch ${prefix}.unmapped.bam
+    echo '' | gzip > ${prefix}.split1.bam
+    echo '' | gzip > ${prefix}.unmapped.bam
     """
 
 }
```

### bamutil/clipoverlap
```diff
--- a/modules/nf-core/bamutil/clipoverlap/main.nf
+++ b/modules/nf-core/bamutil/clipoverlap/main.nf
@@ -35,7 +35,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}_clipoverlap"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.log
     """
 }
```

### bamutil/trimbam
```diff
--- a/modules/nf-core/bamutil/trimbam/main.nf
+++ b/modules/nf-core/bamutil/trimbam/main.nf
@@ -33,7 +33,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}_trimbam"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### bbmap/align
```diff
--- a/modules/nf-core/bbmap/align/main.nf
+++ b/modules/nf-core/bbmap/align/main.nf
@@ -51,7 +51,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.bbmap.log
     """
 }
```

### biobambam/bammarkduplicates2
```diff
--- a/modules/nf-core/biobambam/bammarkduplicates2/main.nf
+++ b/modules/nf-core/biobambam/bammarkduplicates2/main.nf
@@ -34,7 +34,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.metrics.txt
     """
 }
```

### biobambam/bammerge
```diff
--- a/modules/nf-core/biobambam/bammerge/main.nf
+++ b/modules/nf-core/biobambam/bammerge/main.nf
@@ -35,7 +35,7 @@
     prefix = task.ext.prefix ?: "${meta.id}"
 
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### biscuit/align
```diff
--- a/modules/nf-core/biscuit/align/main.nf
+++ b/modules/nf-core/biscuit/align/main.nf
@@ -43,8 +43,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
-    touch ${prefix}.bam.bai
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam.bai
     """
 }
```

### biscuit/biscuitblaster
```diff
--- a/modules/nf-core/biscuit/biscuitblaster/main.nf
+++ b/modules/nf-core/biscuit/biscuitblaster/main.nf
@@ -49,8 +49,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
-    touch ${prefix}.bam.bai
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam.bai
     """
 
 }
```

### biscuit/bsconv
```diff
--- a/modules/nf-core/biscuit/bsconv/main.nf
+++ b/modules/nf-core/biscuit/bsconv/main.nf
@@ -37,7 +37,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
```

### bismark/align
```diff
--- a/modules/nf-core/bismark/align/main.nf
+++ b/modules/nf-core/bismark/align/main.nf
@@ -67,7 +67,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.report.txt
     """
 }
```

### bismark/deduplicate
```diff
--- a/modules/nf-core/bismark/deduplicate/main.nf
+++ b/modules/nf-core/bismark/deduplicate/main.nf
@@ -31,7 +31,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.deduplicated.bam
+    echo '' | gzip > ${prefix}.deduplicated.bam
     touch ${prefix}.deduplication_report.txt
     """
 }
```

### bowtie/align
```diff
--- a/modules/nf-core/bowtie/align/main.nf
+++ b/modules/nf-core/bowtie/align/main.nf
@@ -59,7 +59,7 @@
             "echo '' | gzip > ${prefix}.unmapped_1.fastq.gz; echo '' | gzip > ${prefix}.unmapped_2.fastq.gz" :
                 ''
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.out
     $unaligned
     """
```

### bowtie2/align
```diff
--- a/modules/nf-core/bowtie2/align/main.nf
+++ b/modules/nf-core/bowtie2/align/main.nf
@@ -83,9 +83,9 @@
     def extension = (args2 ==~ extension_pattern) ? (args2 =~ extension_pattern)[0][2].toLowerCase() : "bam"
     def create_unmapped = ""
     if (meta.single_end) {
-        create_unmapped = save_unaligned ? "touch ${prefix}.unmapped.fastq.gz" : ""
+        create_unmapped = save_unaligned ? "echo '' | gzip > ${prefix}.unmapped.fastq.gz" : ""
     } else {
-        create_unmapped = save_unaligned ? "touch ${prefix}.unmapped_1.fastq.gz && touch ${prefix}.unmapped_2.fastq.gz" : ""
+        create_unmapped = save_unaligned ? "echo '' | gzip > ${prefix}.unmapped_1.fastq.gz && echo '' | gzip > ${prefix}.unmapped_2.fastq.gz" : ""
     }
     if (!fasta && extension=="cram") error "Fasta reference is required for CRAM output"
```

### bwa/sampe
```diff
--- a/modules/nf-core/bwa/sampe/main.nf
+++ b/modules/nf-core/bwa/sampe/main.nf
@@ -39,7 +39,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### bwa/samse
```diff
--- a/modules/nf-core/bwa/samse/main.nf
+++ b/modules/nf-core/bwa/samse/main.nf
@@ -38,7 +38,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### bwameth/align
```diff
--- a/modules/nf-core/bwameth/align/main.nf
+++ b/modules/nf-core/bwameth/align/main.nf
@@ -39,7 +39,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### chromap/chromap
```diff
--- a/modules/nf-core/chromap/chromap/main.nf
+++ b/modules/nf-core/chromap/chromap/main.nf
@@ -86,7 +86,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
     echo "" | gzip > ${prefix}.bed.gz
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     echo "" | gzip > ${prefix}.tagAlign.gz
     echo "" | gzip > ${prefix}.pairs.gz
     """
```

### circularmapper/realignsamfile
```diff
--- a/modules/nf-core/circularmapper/realignsamfile/main.nf
+++ b/modules/nf-core/circularmapper/realignsamfile/main.nf
@@ -43,7 +43,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}_realigned.bam
+    echo '' | gzip > ${prefix}_realigned.bam
     """
 }
```

### coptr/map
```diff
--- a/modules/nf-core/coptr/map/main.nf
+++ b/modules/nf-core/coptr/map/main.nf
@@ -46,7 +46,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### coptr/merge
```diff
--- a/modules/nf-core/coptr/merge/main.nf
+++ b/modules/nf-core/coptr/merge/main.nf
@@ -32,7 +32,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### coverm/contig
```diff
--- a/modules/nf-core/coverm/contig/main.nf
+++ b/modules/nf-core/coverm/contig/main.nf
@@ -48,7 +48,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
     touch ${prefix}.depth.tsv
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### coverm/genome
```diff
--- a/modules/nf-core/coverm/genome/main.nf
+++ b/modules/nf-core/coverm/genome/main.nf
@@ -55,7 +55,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
     touch ${prefix}.depth.tsv
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### ctatsplicing/startocancerintrons
```diff
--- a/modules/nf-core/ctatsplicing/startocancerintrons/main.nf
+++ b/modules/nf-core/ctatsplicing/startocancerintrons/main.nf
@@ -53,10 +53,10 @@
     def create_igv_files = args.contains("--vis") ? "touch ${prefix}.introns.for_IGV.bed && touch ${prefix}.ctat-splicing.igv.html && touch ${prefix}.igv.tracks" : ""
     """
     ${create_igv_files}
-    touch ${prefix}.cancer_intron_reads.sorted.bam
-    touch ${prefix}.cancer_intron_reads.sorted.bam.bai
-    touch ${prefix}.gene_reads.sorted.sifted.bam
-    touch ${prefix}.gene_reads.sorted.sifted.bam.bai
+    echo '' | gzip > ${prefix}.cancer_intron_reads.sorted.bam
+    echo '' | gzip > ${prefix}.cancer_intron_reads.sorted.bam.bai
+    echo '' | gzip > ${prefix}.gene_reads.sorted.sifted.bam
+    echo '' | gzip > ${prefix}.gene_reads.sorted.sifted.bam.bai
     touch ${prefix}.cancer.introns
     touch ${prefix}.cancer.introns.prelim
     touch ${prefix}.introns
```

### dedup
```diff
--- a/modules/nf-core/dedup/main.nf
+++ b/modules/nf-core/dedup/main.nf
@@ -44,7 +44,7 @@
     touch ${prefix}.json
     touch ${prefix}.hist
     touch ${prefix}.log
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### deeptools/alignmentsieve
```diff
--- a/modules/nf-core/deeptools/alignmentsieve/main.nf
+++ b/modules/nf-core/deeptools/alignmentsieve/main.nf
@@ -34,7 +34,7 @@
     stub:
     def prefix    = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}_as.bam
+    echo '' | gzip > ${prefix}_as.bam
     touch ${prefix}_log.txt
     """
 }
```

### disambiguate
```diff
--- a/modules/nf-core/disambiguate/main.nf
+++ b/modules/nf-core/disambiguate/main.nf
@@ -36,10 +36,10 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.disambiguatedSpeciesA.bam
-    touch ${prefix}.disambiguatedSpeciesB.bam
-    touch ${prefix}.ambiguousSpeciesA.bam
-    touch ${prefix}.ambiguousSpeciesB.bam
+    echo '' | gzip > ${prefix}.disambiguatedSpeciesA.bam
+    echo '' | gzip > ${prefix}.disambiguatedSpeciesB.bam
+    echo '' | gzip > ${prefix}.ambiguousSpeciesA.bam
+    echo '' | gzip > ${prefix}.ambiguousSpeciesB.bam
     touch ${prefix}_summary.txt
     """
 }
```

### expansionhunter
```diff
--- a/modules/nf-core/expansionhunter/main.nf
+++ b/modules/nf-core/expansionhunter/main.nf
@@ -46,7 +46,7 @@
     """
     echo "" | gzip > ${prefix}.vcf.gz
     echo "" | gzip > ${prefix}.json.gz
-    touch ${prefix}_realigned.bam
+    echo '' | gzip > ${prefix}_realigned.bam
 
     """
 }
```

### fgbio/copyumifromreadname
```diff
--- a/modules/nf-core/fgbio/copyumifromreadname/main.nf
+++ b/modules/nf-core/fgbio/copyumifromreadname/main.nf
@@ -47,7 +47,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}_umi_extracted"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.bai
     """
 }
```

### fibertoolsrs/addnucleosomes
```diff
--- a/modules/nf-core/fibertoolsrs/addnucleosomes/main.nf
+++ b/modules/nf-core/fibertoolsrs/addnucleosomes/main.nf
@@ -43,7 +43,7 @@
     """
     echo $args
 
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### fibertoolsrs/predictm6a
```diff
--- a/modules/nf-core/fibertoolsrs/predictm6a/main.nf
+++ b/modules/nf-core/fibertoolsrs/predictm6a/main.nf
@@ -43,7 +43,7 @@
     """
     echo $args
 
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### gatk4/fastqtosam
```diff
--- a/modules/nf-core/gatk4/fastqtosam/main.nf
+++ b/modules/nf-core/gatk4/fastqtosam/main.nf
@@ -42,7 +42,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### gatk4/haplotypecaller
```diff
--- a/modules/nf-core/gatk4/haplotypecaller/main.nf
+++ b/modules/nf-core/gatk4/haplotypecaller/main.nf
@@ -61,8 +61,8 @@
 
     def stub_realigned_bam = bamout_command ? "touch ${prefix.replaceAll('.g\\s*$', '')}.realigned.bam" : ""
     """
-    touch ${prefix}.vcf.gz
-    touch ${prefix}.vcf.gz.tbi
+    echo '' | gzip > ${prefix}.vcf.gz
+    echo '' | gzip > ${prefix}.vcf.gz.tbi
     ${stub_realigned_bam}
     """
 }
```

### gatk4/markduplicates
```diff
--- a/modules/nf-core/gatk4/markduplicates/main.nf
+++ b/modules/nf-core/gatk4/markduplicates/main.nf
@@ -66,9 +66,9 @@
     prefix = task.ext.prefix ?: "${meta.id}.bam"
     prefix_no_suffix = task.ext.prefix ? prefix.tokenize('.')[0] : "${meta.id}"
     """
-    touch ${prefix_no_suffix}.bam
-    touch ${prefix_no_suffix}.cram
-    touch ${prefix_no_suffix}.cram.crai
+    echo '' | gzip > ${prefix_no_suffix}.bam
+    echo '' | gzip > ${prefix_no_suffix}.cram
+    echo '' | gzip > ${prefix_no_suffix}.cram.crai
     touch ${prefix_no_suffix}.bai
     touch ${prefix}.metrics
     """
```

### gatk4/mergebamalignment
```diff
--- a/modules/nf-core/gatk4/mergebamalignment/main.nf
+++ b/modules/nf-core/gatk4/mergebamalignment/main.nf
@@ -44,7 +44,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### gatk4/revertsam
```diff
--- a/modules/nf-core/gatk4/revertsam/main.nf
+++ b/modules/nf-core/gatk4/revertsam/main.nf
@@ -40,7 +40,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.reverted.bam
+    echo '' | gzip > ${prefix}.reverted.bam
     """
 }
```

### gatk4/splitncigarreads
```diff
--- a/modules/nf-core/gatk4/splitncigarreads/main.nf
+++ b/modules/nf-core/gatk4/splitncigarreads/main.nf
@@ -47,7 +47,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
 
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### gatk4/unmarkduplicates
```diff
--- a/modules/nf-core/gatk4/unmarkduplicates/main.nf
+++ b/modules/nf-core/gatk4/unmarkduplicates/main.nf
@@ -41,7 +41,7 @@
     stub:
     prefix = task.ext.prefix ?: "${meta.id}_UnmarkDuplicates"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.bai
     """
 }
```

### gem3/gem3mapper
```diff
--- a/modules/nf-core/gem3/gem3mapper/main.nf
+++ b/modules/nf-core/gem3/gem3mapper/main.nf
@@ -37,7 +37,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
         gem-mapper: \$(echo \$(gem-mapper --version 2>&1) | sed 's/v//')
```

### hisat2/align
```diff
--- a/modules/nf-core/hisat2/align/main.nf
+++ b/modules/nf-core/hisat2/align/main.nf
@@ -86,7 +86,7 @@
     ${unaligned}
 
     touch ${prefix}.hisat2.summary.log
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 
 }
```

### hlala/typing
```diff
--- a/modules/nf-core/hlala/typing/main.nf
+++ b/modules/nf-core/hlala/typing/main.nf
@@ -64,12 +64,12 @@
     touch results/R_1.fastq
     touch results/R_2.fastq
     touch results/R_U.fastq
-    touch results/extraction.bam
-    touch results/extraction.bam.bai
-    touch results/extraction_mapped.bam
-    touch results/extraction_unmapped.bam
-    touch results/remapped_with_a.bam
-    touch results/remapped_with_a.bam.bai
+    echo '' | gzip > results/extraction.bam
+    echo '' | gzip > results/extraction.bam.bai
+    echo '' | gzip > results/extraction_mapped.bam
+    echo '' | gzip > results/extraction_unmapped.bam
+    echo '' | gzip > results/remapped_with_a.bam
+    echo '' | gzip > results/remapped_with_a.bam.bai
     touch results/reads_per_level.txt
 
     mkdir results/hla
```

### isoseq/cluster
```diff
--- a/modules/nf-core/isoseq/cluster/main.nf
+++ b/modules/nf-core/isoseq/cluster/main.nf
@@ -46,8 +46,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.transcripts.bam
-    touch ${prefix}.transcripts.bam.pbi
+    echo '' | gzip > ${prefix}.transcripts.bam
+    echo '' | gzip > ${prefix}.transcripts.bam.pbi
     touch ${prefix}.transcripts.cluster
     touch ${prefix}.transcripts.cluster_report.csv
     touch ${prefix}.transcripts.transcriptset.xml
```

### isoseq/refine
```diff
--- a/modules/nf-core/isoseq/refine/main.nf
+++ b/modules/nf-core/isoseq/refine/main.nf
@@ -43,8 +43,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
-    touch ${prefix}.bam.pbi
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam.pbi
     touch ${prefix}.consensusreadset.xml
     touch ${prefix}.filter_summary.report.json
     touch ${prefix}.report.csv
```

### isoseq3/tag
```diff
--- a/modules/nf-core/isoseq3/tag/main.nf
+++ b/modules/nf-core/isoseq3/tag/main.nf
@@ -42,8 +42,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.flt.bam
-    touch ${prefix}.flt.bam.pbi
+    echo '' | gzip > ${prefix}.flt.bam
+    echo '' | gzip > ${prefix}.flt.bam.pbi
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### ivar/trim
```diff
--- a/modules/nf-core/ivar/trim/main.nf
+++ b/modules/nf-core/ivar/trim/main.nf
@@ -40,7 +40,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
     touch ${prefix}.ivar.log
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### leehom
```diff
--- a/modules/nf-core/leehom/main.nf
+++ b/modules/nf-core/leehom/main.nf
@@ -82,7 +82,7 @@
 
     """
     if [[ "${is_bam}" == "true" ]]; then
-        touch ${prefix}.bam
+        echo '' | gzip > ${prefix}.bam
     else
         echo "" | gzip > ${prefix}.fq.gz
         echo "" | gzip > ${prefix}.fail.fq.gz
```

### leviosam2/lift
```diff
--- a/modules/nf-core/leviosam2/lift/main.nf
+++ b/modules/nf-core/leviosam2/lift/main.nf
@@ -40,7 +40,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### lofreq/alnqual
```diff
--- a/modules/nf-core/lofreq/alnqual/main.nf
+++ b/modules/nf-core/lofreq/alnqual/main.nf
@@ -41,7 +41,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### lofreq/indelqual
```diff
--- a/modules/nf-core/lofreq/indelqual/main.nf
+++ b/modules/nf-core/lofreq/indelqual/main.nf
@@ -37,7 +37,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### lofreq/viterbi
```diff
--- a/modules/nf-core/lofreq/viterbi/main.nf
+++ b/modules/nf-core/lofreq/viterbi/main.nf
@@ -43,7 +43,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### metamdbg/asm
```diff
--- a/modules/nf-core/metamdbg/asm/main.nf
+++ b/modules/nf-core/metamdbg/asm/main.nf
@@ -44,7 +44,7 @@
     """
     echo ${args}
     touch ${prefix}.metaMDBG.log
-    touch ${prefix}.contigs.fasta.gz
+    echo '' | gzip > ${prefix}.contigs.fasta.gz
     """
 }
```

### modkit/callmods
```diff
--- a/modules/nf-core/modkit/callmods/main.nf
+++ b/modules/nf-core/modkit/callmods/main.nf
@@ -41,7 +41,7 @@
     """
     echo ${args}
 
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.log
     """
 }
```

### modkit/repair
```diff
--- a/modules/nf-core/modkit/repair/main.nf
+++ b/modules/nf-core/modkit/repair/main.nf
@@ -39,7 +39,7 @@
     """
     echo ${args}
 
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.log
     """
 }
```

### mudskipper/bulk
```diff
--- a/modules/nf-core/mudskipper/bulk/main.nf
+++ b/modules/nf-core/mudskipper/bulk/main.nf
@@ -50,7 +50,7 @@
     stub:
     prefix = task.ext.prefix ?: "${meta.id}.transcriptome"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### nextgenmap
```diff
--- a/modules/nf-core/nextgenmap/main.nf
+++ b/modules/nf-core/nextgenmap/main.nf
@@ -59,7 +59,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### parabricks/applybqsr
```diff
--- a/modules/nf-core/parabricks/applybqsr/main.nf
+++ b/modules/nf-core/parabricks/applybqsr/main.nf
@@ -47,8 +47,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
-    touch ${prefix}.bam.bai
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam.bai
     """
 }
```

### paraphase
```diff
--- a/modules/nf-core/paraphase/main.nf
+++ b/modules/nf-core/paraphase/main.nf
@@ -66,10 +66,10 @@
     mkdir ${prefix}_paraphase_vcfs
 
     touch ${prefix}.paraphase.json
-    touch ${prefix}.paraphase.bam
-    touch ${prefix}.paraphase.bam.bai
+    echo '' | gzip > ${prefix}.paraphase.bam
+    echo '' | gzip > ${prefix}.paraphase.bam.bai
     echo '' | gzip > ${prefix}_paraphase_vcfs/${prefix}_stub.vcf.gz
-    touch ${prefix}_paraphase_vcfs/${prefix}_stub.vcf.gz.${index}
+    echo '' | gzip > ${prefix}_paraphase_vcfs/${prefix}_stub.vcf.gz.${index}
     """
 }
```

### pbbam/pbmerge
```diff
--- a/modules/nf-core/pbbam/pbmerge/main.nf
+++ b/modules/nf-core/pbbam/pbmerge/main.nf
@@ -52,8 +52,8 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     assert false: deprecation_message
     """
-    touch ${prefix}.bam
-    touch ${prefix}.bam.pbi
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam.pbi
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### pbccs
```diff
--- a/modules/nf-core/pbccs/main.nf
+++ b/modules/nf-core/pbccs/main.nf
@@ -46,8 +46,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.chunk1.bam
-    touch ${prefix}.chunk1.bam.pbi
+    echo '' | gzip > ${prefix}.chunk1.bam
+    echo '' | gzip > ${prefix}.chunk1.bam.pbi
     touch ${prefix}.report.txt
     touch ${prefix}.report.json
     echo | gzip > ${prefix}.metrics.json.gz
```

### pbjasmine
```diff
--- a/modules/nf-core/pbjasmine/main.nf
+++ b/modules/nf-core/pbjasmine/main.nf
@@ -42,7 +42,7 @@
     """
     echo $args
 
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### pbmm2/align
```diff
--- a/modules/nf-core/pbmm2/align/main.nf
+++ b/modules/nf-core/pbmm2/align/main.nf
@@ -40,7 +40,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### pbtk/pbmerge
```diff
--- a/modules/nf-core/pbtk/pbmerge/main.nf
+++ b/modules/nf-core/pbtk/pbmerge/main.nf
@@ -37,8 +37,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
-    touch ${prefix}.bam.pbi
+    echo '' | gzip > ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam.pbi
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### pharmcat/vcfpreprocessor
```diff
--- a/modules/nf-core/pharmcat/vcfpreprocessor/main.nf
+++ b/modules/nf-core/pharmcat/vcfpreprocessor/main.nf
@@ -41,7 +41,7 @@
     """
     echo $args
 
-    touch ${prefix}.preprocessed.vcf.bgz
+    echo '' | gzip > ${prefix}.preprocessed.vcf.bgz
     touch ${prefix}.missing_pgx_var.vcf
     """
 }
```

### pharokka/installdatabases
```diff
--- a/modules/nf-core/pharokka/installdatabases/main.nf
+++ b/modules/nf-core/pharokka/installdatabases/main.nf
@@ -41,7 +41,7 @@
     touch $prefix/CARD_h
     touch $prefix/CARD_h.dbtype
     touch $prefix/CARD_h.index
-    touch $prefix/VFDB_setB_pro.fas.gz
+    echo '' | gzip > $prefix/VFDB_setB_pro.fas.gz
     touch $prefix/VFDBclusterRes_cluster.tsv
     touch $prefix/VFDBclusterRes_rep_seq.fasta
     touch $prefix/all_phrogs.h3m
```

### picard/fastqtosam
```diff
--- a/modules/nf-core/picard/fastqtosam/main.nf
+++ b/modules/nf-core/picard/fastqtosam/main.nf
@@ -39,7 +39,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### picard/mergesamfiles
```diff
--- a/modules/nf-core/picard/mergesamfiles/main.nf
+++ b/modules/nf-core/picard/mergesamfiles/main.nf
@@ -47,7 +47,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### picard/positionbaseddownsamplesam
```diff
--- a/modules/nf-core/picard/positionbaseddownsamplesam/main.nf
+++ b/modules/nf-core/picard/positionbaseddownsamplesam/main.nf
@@ -47,8 +47,8 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.ds10.bam
-    touch ${prefix}.ds10.bam.bai
+    echo '' | gzip > ${prefix}.ds10.bam
+    echo '' | gzip > ${prefix}.ds10.bam.bai
     """
 }
```

### picard/setnmmdanduqtags
```diff
--- a/modules/nf-core/picard/setnmmdanduqtags/main.nf
+++ b/modules/nf-core/picard/setnmmdanduqtags/main.nf
@@ -44,7 +44,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.bai
     """
 }
```

### pmdtools/filter
```diff
--- a/modules/nf-core/pmdtools/filter/main.nf
+++ b/modules/nf-core/pmdtools/filter/main.nf
@@ -58,7 +58,7 @@
     if ("$bam" == "${prefix}.bam") error "[pmdtools/filter] Input and output names are the same, use \"task.ext.prefix\" to disambiguate!"
     //threshold and header flags activate filtering function of pmdtools
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### popscle/freemuxlet
```diff
--- a/modules/nf-core/popscle/freemuxlet/main.nf
+++ b/modules/nf-core/popscle/freemuxlet/main.nf
@@ -44,13 +44,13 @@
     def VERSION = '0.1' // WARN: Version information not provided by tool on CLI. Please update version string below when bumping container versions.
 
     """
-    touch ${prefix}.clust1.samples.gz
-    touch ${prefix}.clust1.vcf.gz
+    echo '' | gzip > ${prefix}.clust1.samples.gz
+    echo '' | gzip > ${prefix}.clust1.vcf.gz
     touch ${prefix}.lmix
 
     if [[ "$args" == *"--aux-files"* ]]; then
-        touch ${prefix}.clust0.samples.gz
-        touch ${prefix}.clust0.vcf.gz
+        echo '' | gzip > ${prefix}.clust0.samples.gz
+        echo '' | gzip > ${prefix}.clust0.vcf.gz
     fi
 
     cat <<-END_VERSIONS > versions.yml
```

### portello
```diff
--- a/modules/nf-core/portello/main.nf
+++ b/modules/nf-core/portello/main.nf
@@ -40,13 +40,13 @@
     stub:
     def args = task.ext.args ?: ''
     def prefix = task.ext.prefix ?: "${meta.id}"
-    def vcf_output = output_vcf ? "echo | gzip -c > ${prefix}.vcf.gz; touch ${prefix}.vcf.gz.tbi" : ''
+    def vcf_output = output_vcf ? "echo | gzip -c > ${prefix}.vcf.gz; echo '' | gzip > ${prefix}.vcf.gz.tbi" : ''
     """
     echo ${args}
 
     ${vcf_output}
-    touch ${prefix}_unassembled.bam
-    touch ${prefix}_remapped.bam
+    echo '' | gzip > ${prefix}_unassembled.bam
+    echo '' | gzip > ${prefix}_remapped.bam
     """
 }
```

### rastair/methylkit
```diff
--- a/modules/nf-core/rastair/methylkit/main.nf
+++ b/modules/nf-core/rastair/methylkit/main.nf
@@ -31,7 +31,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.methylkit.txt.gz
+    echo '' | gzip > ${prefix}.methylkit.txt.gz
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### rsem/calculateexpression
```diff
--- a/modules/nf-core/rsem/calculateexpression/main.nf
+++ b/modules/nf-core/rsem/calculateexpression/main.nf
@@ -81,11 +81,11 @@
 
     # Only create STAR BAM output when not in alignment mode
     if [ "${is_bam}" == "false" ]; then
-        touch ${prefix}.STAR.genome.bam
+        echo '' | gzip > ${prefix}.STAR.genome.bam
     fi
 
-    touch ${prefix}.genome.bam
-    touch ${prefix}.transcript.bam
+    echo '' | gzip > ${prefix}.genome.bam
+    echo '' | gzip > ${prefix}.transcript.bam
     """
 }
```

### rseqc/splitbam
```diff
--- a/modules/nf-core/rseqc/splitbam/main.nf
+++ b/modules/nf-core/rseqc/splitbam/main.nf
@@ -35,9 +35,9 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.in.bam
-    touch ${prefix}.ex.bam
-    touch ${prefix}.junk.bam
+    echo '' | gzip > ${prefix}.in.bam
+    echo '' | gzip > ${prefix}.ex.bam
+    echo '' | gzip > ${prefix}.junk.bam
     """
 }
```

### samtools/ampliconclip
```diff
--- a/modules/nf-core/samtools/ampliconclip/main.nf
+++ b/modules/nf-core/samtools/ampliconclip/main.nf
@@ -46,7 +46,7 @@
     stub:
 
     def prefix = task.ext.prefix ?: "${meta.id}"
-    def rejects = save_cliprejects ? "touch ${prefix}.cliprejects.bam" : ""
+    def rejects = save_cliprejects ? "echo '' | gzip > ${prefix}.cliprejects.bam" : ""
     def stats = save_clipstats ? "touch ${prefix}.clipstats.txt" : ""
 
     if ("${bam}" == "${prefix}.bam") {
```

### samtools/calmd
```diff
--- a/modules/nf-core/samtools/calmd/main.nf
+++ b/modules/nf-core/samtools/calmd/main.nf
@@ -36,7 +36,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### samtools/import
```diff
--- a/modules/nf-core/samtools/import/main.nf
+++ b/modules/nf-core/samtools/import/main.nf
@@ -52,7 +52,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
 
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### samtools/reheader
```diff
--- a/modules/nf-core/samtools/reheader/main.nf
+++ b/modules/nf-core/samtools/reheader/main.nf
@@ -35,7 +35,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### sawfish/discover
```diff
--- a/modules/nf-core/sawfish/discover/main.nf
+++ b/modules/nf-core/sawfish/discover/main.nf
@@ -77,8 +77,8 @@
     touch ${prefix}/candidate.sv.bcf
     touch ${prefix}/candidate.sv.bcf.csi
     touch ${prefix}/assembly.regions.bed
-    touch ${prefix}/contig.alignment.bam
-    touch ${prefix}/contig.alignment.bam.csi
+    echo '' | gzip > ${prefix}/contig.alignment.bam
+    echo '' | gzip > ${prefix}/contig.alignment.bam.csi
     touch ${prefix}/debug.breakpoint_clusters.bed
     touch ${prefix}/debug.cluster.refinement.txt
     touch ${prefix}/discover.settings.json
```

### sawfish/jointcall
```diff
--- a/modules/nf-core/sawfish/jointcall/main.nf
+++ b/modules/nf-core/sawfish/jointcall/main.nf
@@ -65,9 +65,9 @@
     """
     mkdir -p ${prefix}/samples/sample0001_test/
     echo \"\" | gzip > ${prefix}/${prefix}_genotyped.sv.vcf.gz
-    touch ${prefix}/${prefix}_genotyped.sv.vcf.gz.tbi
-    touch ${prefix}/contig.alignment.bam
-    touch ${prefix}/contig.alignment.bam.csi
+    echo '' | gzip > ${prefix}/${prefix}_genotyped.sv.vcf.gz.tbi
+    echo '' | gzip > ${prefix}/contig.alignment.bam
+    echo '' | gzip > ${prefix}/contig.alignment.bam.csi
     touch ${prefix}/run.stats.json
     touch ${prefix}/sawfish.log
     touch ${prefix}/samples/sample0001_test/copynum.bedgraph
```

### sentieon/rsemcalculateexpression
```diff
--- a/modules/nf-core/sentieon/rsemcalculateexpression/main.nf
+++ b/modules/nf-core/sentieon/rsemcalculateexpression/main.nf
@@ -98,11 +98,11 @@
 
     # Only create STAR BAM output when not in alignment mode
     if [ "${is_bam}" == "false" ]; then
-        touch ${prefix}.STAR.genome.bam
+        echo '' | gzip > ${prefix}.STAR.genome.bam
     fi
 
-    touch ${prefix}.genome.bam
-    touch ${prefix}.transcript.bam
+    echo '' | gzip > ${prefix}.genome.bam
+    echo '' | gzip > ${prefix}.transcript.bam
     """
 }
```

### sentieon/staralign
```diff
--- a/modules/nf-core/sentieon/staralign/main.nf
+++ b/modules/nf-core/sentieon/staralign/main.nf
@@ -82,14 +82,14 @@
     """
     echo "" | gzip > ${prefix}.unmapped_1.fastq.gz
     echo "" | gzip > ${prefix}.unmapped_2.fastq.gz
-    touch ${prefix}Xd.out.bam
+    echo '' | gzip > ${prefix}Xd.out.bam
     touch ${prefix}.Log.final.out
     touch ${prefix}.Log.out
     touch ${prefix}.Log.progress.out
-    touch ${prefix}.sortedByCoord.out.bam
-    touch ${prefix}.toTranscriptome.out.bam
-    touch ${prefix}.Aligned.unsort.out.bam
-    touch ${prefix}.Aligned.sortedByCoord.out.bam
+    echo '' | gzip > ${prefix}.sortedByCoord.out.bam
+    echo '' | gzip > ${prefix}.toTranscriptome.out.bam
+    echo '' | gzip > ${prefix}.Aligned.unsort.out.bam
+    echo '' | gzip > ${prefix}.Aligned.sortedByCoord.out.bam
     touch ${prefix}.tab
     touch ${prefix}.SJ.out.tab
     touch ${prefix}.ReadsPerGene.out.tab
```

### slamdunk/all
```diff
--- a/modules/nf-core/slamdunk/all/main.nf
+++ b/modules/nf-core/slamdunk/all/main.nf
@@ -54,9 +54,9 @@
     mkdir -p outputs/snp
     mkdir -p outputs/count
 
-    touch outputs/map/${prefix}.bam
-    touch outputs/filter/${prefix}_filtered.bam
-    touch outputs/filter/${prefix}_filtered.bam.bai
+    echo '' | gzip > outputs/map/${prefix}.bam
+    echo '' | gzip > outputs/filter/${prefix}_filtered.bam
+    echo '' | gzip > outputs/filter/${prefix}_filtered.bam.bai
     touch outputs/snp/${prefix}.vcf
     touch outputs/count/${prefix}.tsv
     touch outputs/count/${prefix}_plus.bedgraph
```

### snapaligner/align
```diff
--- a/modules/nf-core/snapaligner/align/main.nf
+++ b/modules/nf-core/snapaligner/align/main.nf
@@ -38,8 +38,8 @@
 
     stub:
     """
-    touch test.bam
-    touch test.bam.bai
+    echo '' | gzip > test.bam
+    echo '' | gzip > test.bam.bai
     """
 }
```

### snippy/run
```diff
--- a/modules/nf-core/snippy/run/main.nf
+++ b/modules/nf-core/snippy/run/main.nf
@@ -64,8 +64,8 @@
     touch ${prefix}/${prefix}.vcf
     touch ${prefix}/${prefix}.bed
     touch ${prefix}/${prefix}.gff
-    touch ${prefix}/${prefix}.bam
-    touch ${prefix}/${prefix}.bam.bai
+    echo '' | gzip > ${prefix}/${prefix}.bam
+    echo '' | gzip > ${prefix}/${prefix}.bam.bai
     touch ${prefix}/${prefix}.log
     touch ${prefix}/${prefix}.aligned.fa
     touch ${prefix}/${prefix}.consensus.fa
@@ -73,7 +73,7 @@
     touch ${prefix}/${prefix}.raw.vcf
     touch ${prefix}/${prefix}.filt.vcf
     gzip -c ${prefix}/${prefix}.vcf > ${prefix}/${prefix}.vcf.gz
-    touch ${prefix}/${prefix}.vcf.gz.csi
+    echo '' | gzip > ${prefix}/${prefix}.vcf.gz.csi
     touch ${prefix}/${prefix}.txt
```

### star/align
```diff
--- a/modules/nf-core/star/align/main.nf
+++ b/modules/nf-core/star/align/main.nf
@@ -76,14 +76,14 @@
     """
     echo "" | gzip > ${prefix}.unmapped_1.fastq.gz
     echo "" | gzip > ${prefix}.unmapped_2.fastq.gz
-    touch ${prefix}Xd.out.bam
+    echo '' | gzip > ${prefix}Xd.out.bam
     touch ${prefix}.Log.final.out
     touch ${prefix}.Log.out
     touch ${prefix}.Log.progress.out
-    touch ${prefix}.sortedByCoord.out.bam
-    touch ${prefix}.toTranscriptome.out.bam
-    touch ${prefix}.Aligned.unsort.out.bam
-    touch ${prefix}.Aligned.sortedByCoord.out.bam
+    echo '' | gzip > ${prefix}.sortedByCoord.out.bam
+    echo '' | gzip > ${prefix}.toTranscriptome.out.bam
+    echo '' | gzip > ${prefix}.Aligned.unsort.out.bam
+    echo '' | gzip > ${prefix}.Aligned.sortedByCoord.out.bam
     touch ${prefix}.tab
     touch ${prefix}.SJ.out.tab
     touch ${prefix}.ReadsPerGene.out.tab
```

### staramr/search
```diff
--- a/modules/nf-core/staramr/search/main.nf
+++ b/modules/nf-core/staramr/search/main.nf
@@ -52,8 +52,8 @@
     """
     mkdir ${prefix}_results
     touch ${prefix}_results/results.xlsx
-    touch ${prefix}_results/{summary,detailed_summary,resfinder,pointfinder,plasmidfinder,mlst}.tsv.gz
-    touch ${prefix}_results/settings.txt.gz
+    echo '' | gzip > ${prefix}_results/{summary,detailed_summary,resfinder,pointfinder,plasmidfinder,mlst}.tsv.gz
+    echo '' | gzip > ${prefix}_results/settings.txt.gz
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### svtyper/svtyper
```diff
--- a/modules/nf-core/svtyper/svtyper/main.nf
+++ b/modules/nf-core/svtyper/svtyper/main.nf
@@ -48,7 +48,7 @@
     """
     touch ${prefix}.json
     touch ${prefix}.vcf
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### tagbam
```diff
--- a/modules/nf-core/tagbam/main.nf
+++ b/modules/nf-core/tagbam/main.nf
@@ -31,7 +31,7 @@
     stub:
     prefix   = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     """
 }
```

### telescope/assign
```diff
--- a/modules/nf-core/telescope/assign/main.nf
+++ b/modules/nf-core/telescope/assign/main.nf
@@ -45,8 +45,8 @@
     """
     echo $args
 
-    touch ${prefix}-updated.bam
-    touch ${prefix}-other.bam
+    echo '' | gzip > ${prefix}-updated.bam
+    echo '' | gzip > ${prefix}-other.bam
     touch ${prefix}-updated.sam
     touch ${prefix}-other.sam
     touch ${prefix}-telescope_report.tsv
```

### trgt/genotype
```diff
--- a/modules/nf-core/trgt/genotype/main.nf
+++ b/modules/nf-core/trgt/genotype/main.nf
@@ -44,7 +44,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.spanning.bam
+    echo '' | gzip > ${prefix}.spanning.bam
     echo "" | gzip > ${prefix}.vcf.gz
 
     cat <<-END_VERSIONS > versions.yml
```

### ultra/align
```diff
--- a/modules/nf-core/ultra/align/main.nf
+++ b/modules/nf-core/ultra/align/main.nf
@@ -54,7 +54,7 @@
     stub:
     def prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
         ultra: \$( uLTRA --version|sed 's/uLTRA //g' )
```

### umitools/dedup
```diff
--- a/modules/nf-core/umitools/dedup/main.nf
+++ b/modules/nf-core/umitools/dedup/main.nf
@@ -47,7 +47,7 @@
     stub:
     prefix = task.ext.prefix ?: "${meta.id}"
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     touch ${prefix}.log
     touch ${prefix}_edit_distance.tsv
     touch ${prefix}_per_umi.tsv
```

### umitools/prepareforrsem
```diff
--- a/modules/nf-core/umitools/prepareforrsem/main.nf
+++ b/modules/nf-core/umitools/prepareforrsem/main.nf
@@ -32,7 +32,7 @@
 
     stub:
     """
-    touch ${meta.id}.bam
+    echo '' | gzip > ${meta.id}.bam
     touch ${meta.id}.log
     """
 }
```

### variantbam
```diff
--- a/modules/nf-core/variantbam/main.nf
+++ b/modules/nf-core/variantbam/main.nf
@@ -37,7 +37,7 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     def VERSION = '1.4.4a' // WARN: Version information not provided by tool on CLI. Please update this string when bumping container versions.
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
 
     cat <<-END_VERSIONS > versions.yml
     "${task.process}":
```

### whatshap/haplotag
```diff
--- a/modules/nf-core/whatshap/haplotag/main.nf
+++ b/modules/nf-core/whatshap/haplotag/main.nf
@@ -47,7 +47,7 @@
 
     def output_tsv = include_tsv_output  ? "echo '' | gzip > ${prefix}.tsv.gz" : ''
     """
-    touch ${prefix}.bam
+    echo '' | gzip > ${prefix}.bam
     $output_tsv
 
     echo $args
```

### yara/mapper
```diff
--- a/modules/nf-core/yara/mapper/main.nf
+++ b/modules/nf-core/yara/mapper/main.nf
@@ -68,8 +68,8 @@
     def prefix = task.ext.prefix ?: "${meta.id}"
     if (meta.single_end) {
         """
-        touch ${prefix}.mapped.bam
-        touch ${prefix}.mapped.bam.bai
+        echo '' | gzip > ${prefix}.mapped.bam
+        echo '' | gzip > ${prefix}.mapped.bam.bai
 
         cat <<-END_VERSIONS > versions.yml
         "${task.process}":
@@ -79,8 +79,8 @@
         """
     } else {
         """
-        touch ${prefix}_1.mapped.bam
-        touch ${prefix}_2.mapped.bam.bai
+        echo '' | gzip > ${prefix}_1.mapped.bam
+        echo '' | gzip > ${prefix}_2.mapped.bam.bai
 
         cat <<-END_VERSIONS > versions.yml
         "${task.process}":
```

### vt/decomposeblocksub
```diff
--- a/modules/nf-core/vt/decomposeblocksub/main.nf
+++ b/modules/nf-core/vt/decomposeblocksub/main.nf
@@ -51,7 +51,7 @@
     """
-    touch ${prefix}.vcf.gz
+    echo '' | gzip > ${prefix}.vcf.gz
 
     cat <<-END_VERSIONS > versions.yml
```


**Total Modules Processed:** 120