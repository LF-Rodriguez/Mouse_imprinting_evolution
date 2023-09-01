## K-padre

*K-padre* was designed to classify WGBS reads according to their parental origin using diagnostic sequence variants. 
The python script takes two input files, a list of variants produced by the complementary script K-variant, 
and an alignment file (SAM/BAM) with WGBS reads mapped to one of the parental genomes. The output is a SAM file with
additional columns that indicate the most likely allelic origin of each alignment and the number of variants that 
support its assignation. To reduce reference bias, it is recommended to run K-padre twice, using reads aligned to 
each parental genome or pseudogenome as reference. The outputs of each run can be processed by k-reads to identify
reads that consistently show evidence of the same parental origin in both alignments.

!(./k_padre_pipeline.png)

### Generation of diagnostic variants file for k-padre
To identify diagnostic variants, k-variant uses a VCF file containing variants unique to one parent with respect to 
the other parent’s genome. In the diagram and in the example script below, parents are assigned the IDs P1 and P2 and
these IDs are used as suffix of the VCF file to indicate that it was generated using the parent P1 genome as a 
reference. K-variant filters variants to remove variation potentially induced by the bisulphite DNA transformation 
process and creates a file suited for rapid screening by K-padre. Below is the syntax to use the k-variant script.

`python k-variant.py varaints_P1.vcf variants_P1.txt`

### Assignment of parental origin of SAM records
Once the variant file has been generated, *K-padre* can take it as an input along with a WGSB SAM/BAM alignment file to
assign parent of origin of each alignment record. Both the VCF and the alignment files should be generated using the same
reference genome. *K-padre* utilizes three positional arguments: input alignment fie (SAM/BAM), variants file, and output 
format (“*sam*”,”*bam*”) and creates an output alignment file keeping the same input file name with a “*_KP*” suffix.

`python k-padre.py alignment_P1.sam variants_P1.vcf sam`

The output (“*alignment_P1_KP.sam*”) is a copy of the original alignment file with three additional columns indicating 
parent of origin of each alignment and number of sites supporting origin from parents one or two. 

* g1: (Integer) Indicates number of sites in alignment supporting origin from the reference genome (parent 1)
* g2: (integer) Indicates number of sites in alignment supporting origin from parent 2
* po: (integer) Assignment of parental origin for alignment. 0 = not assigned, 1 = assigned to parent 1, 2 = assigned to parent 2

#### Assignment of parental origin to reads and reduction of mapping bias.
The output of k-padre can be used to select alignments supporting origin from each of the parental genome, however, it 
does not assign parent of origin to individual reads. Additionally, read assignment can be biased towards the reference 
genome due to mapping bias. To assign parent of origin to reads and reduce the effect of mapping bias, K-padre should be 
also run on alignments to the other parent using a VCF file with variants of P1 with respect to the P2 genome:

`python k-variant.py varaints_P2.vcf variants_P2.txt`
`python k-padre.py alignment_P1.sam variants_P2.vcf sam`

The output of the second run of K-padre can be used as input to K-reads along with the input from the first run to assign 
parental origin to reads and reduce the effect of reference bias. K-reads takes two arguments:

`python k-reads.py alignments_P1_KP.sam alignments_P2_KP.sam`

The output of k-reads is two lists of read IDs, one for each parent and whose parental origin was consistently assigned to 
the same parent in both runs.

