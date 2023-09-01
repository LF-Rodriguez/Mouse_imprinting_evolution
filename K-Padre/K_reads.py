## -------------------------------------------------------
## K_reads: scan parent-specific alignemnts and parent 
##	    assignment to identify reads consistently
##	    assigned to each parent.
##
##	    input: alignment_parent1_KP.sam
##	           alignment_parent2_KP.sam 
##	    output: reads_parent1.txt
##		    reads_parent2.txt
##
## -------------------------------------------------------

## -------------------------------------------------------
## Set up environment
## -------------------------------------------------------

# import modules .........................................
import sys
import subprocess

## -------------------------------------------------------
## Obtain input and output files
## -------------------------------------------------------
sam_parent1 = sys.argv[1]
sam_parent2 = sys.argv[2]

## -------------------------------------------------------
## Obtain file name
## -------------------------------------------------------
sample = sam_parent1[:-7]

## -------------------------------------------------------
## Generate temporary file containing parent-assigened 
## reads from each reference alignment
## -------------------------------------------------------

# Collect read asignment data from alignment to parent 1
comand_01 = 'samtools view -F 256 ' + sam_parent1 + ' | grep po:i:1 | cut -f1 > ' + sample + 'parent1_tmp_KR.txt'
comand_02 = 'samtools view -f 256 ' + sam_parent1 + ' | grep po:i:2 | cut -f1 > ' + sample + 'parent2_tmp_KR.txt'

# Complement with assignment from alignment to parent 2
comand_03 = 'samtools view -F 256 ' + sam_parent2 + ' | grep po:i:1 | cut -f1 >> ' + sample + 'parent2_tmp_KR.txt'
comand_04 = 'samtools view -f 256 ' + sam_parent2 + ' | grep po:i:2 | cut -f1 >> ' + sample + 'parent1_tmp_KR.txt'

# Execute bash commands
subprocess.call(comand_01, shell = True)
subprocess.call(comand_02, shell = True)
subprocess.call(comand_03, shell = True)
subprocess.call(comand_04, shell = True)

## -------------------------------------------------------
## Scan files and create lists of reads assigned 
## to each parent
## -------------------------------------------------------

# Obtain first elements of read ID (common to all reads)
with open (sample + 'parent1_tmp_KR.txt', 'r') as fh:
	
	# Extract: instrument, run, flow cell
	line = fh.readline().strip()
	int_run_flowC = ':'.join(line.split(':')[:3])

# Collect read IDs from reads assigned to parent 1
with open (sample + 'parent1_tmp_KR.txt', 'r') as fh:

	P1_reads = []	

	for line in fh.readlines():
		id = ':'.join(line.strip().split(':')[3:])
		P1_reads.append(id)

# Collect read IDs from reads assigned to parent 2
with open (sample + 'parent2_tmp_KR.txt', 'r') as fh:

	P2_reads = []

	for line in fh.readlines():
		id = ':'.join(line.strip().split(':')[3:])
		P2_reads.append(id)

## ---------------------------------------------------------
## Generate lists of unique read IDs assigned to each parent
## ---------------------------------------------------------

# Exclude duplicates
P1_set = set(P1_reads)
P2_set = set(P2_reads)

# Identify reads with discordant assignment
discordant = P1_set.intersection(P2_set)

# Identify reads uniquely assigned to Parents
P1 = P1_set - discordant
P2 = P2_set - discordant

## ----------------------------------------------------------
## collect stats and write output
## ----------------------------------------------------------

# print summary 
print ('reads assigned to parent 1 : ' + str(len(P1)))
print ('reads assigned to parent 2 : ' + str(len(P2)))
print ('discordant reads: ' + str(len(discordant)))

# Write output files 
with open(sample + '_readsP1_KR.txt', 'w') as fh:
	for read in P1:
		fh.write(int_run_flowC + ':' + read +'\n')

with open(sample + '_readsP2_KR.txt', 'w') as fh:
	for read in P2:
		fh.write(int_run_flowC + ':' + read +'\n')

## -------------------------------------------------
## Remove temporary files
## -------------------------------------------------
comand_05 = 'rm '+ sample + 'parent1_tmp_KR.txt'
comand_06 = 'rm '+ sample + 'parent2_tmp_KR.txt'

subprocess.call(comand_05, shell = True)
subprocess.call(comand_06, shell = True)
