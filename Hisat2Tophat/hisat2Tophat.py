## ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
##
## hisat2tophat: Takes a sam file generated by a Hisat2 alignment and
## 		 estimates the Quality Hit index column (HI) to match
##		 the Tophat format, required by Suspenders.
##
## ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

### ------------------------------------------------------------------------
### Set up environment
### ------------------------------------------------------------------------

## import modules
import sys
import subprocess
import re
from datetime import datetime

## read user arguments
inBam  = sys.argv[1]
outBam = sys.argv[2]

## Grab file ID
fileID = inBam[:-4]

### ------------------------------------------------------------------------
### Create functions to read sam flag
### ------------------------------------------------------------------------

def is_mapped(flag):
	'Returns True if read is mapped'

	binary = bin(flag)
	num    = binary[-3]
	if num == '0':
		return True
	else:
		return False

def which_pair(flag):
	'Returns sufix for pairs 1 and 2'

	binary = bin(flag)
	if binary[-7] == '1':
		return '_1'
	else:
		return '_2'

def timer():
	t = datetime.now().strftime("%D:%H:%M:%S")
	time = ' '+t
	return time

### ------------------------------------------------------------------------
### Check Bam file and sort if needed
### ------------------------------------------------------------------------

## Check if file is in correct format
comand1 = 'samtools view -h ' + inBam + ' 2> /dev/null | head -n 1 > '+ fileID +'.header.hisat2tophat.tmp.txt'

subprocess.call(comand1, shell = True)

fh0 = open(fileID + '.header.hisat2tophat.tmp.txt', 'r')

try:
	sorted = fh0.readline().strip().split()[-1].split(':')[-1]
except:
	print( timer() + ' File does not have sorting information in first')
	print( timer() + ' line or is not in BAM format. Please make sure')
	print( timer() + ' input file is in BAM format.')
	sys.exit()

## Check if file is sorted
if sorted != 'coordinate':
	print( timer() + ' File is not sorted by coordinate.')
	print( timer() + ' Sorting file using Samtools')

	# Sort file
	comand2 = 'samtools sort ' + inBam + ' > ' + fileID + '.sortedByCoord.hisat2tophat.tmp.bam'
	subprocess.call(comand2, shell = True)

	# determine which file name to use
	inputBam = fileID + '.sortedByCoord.hisat2tophat.tmp.bam'

	print( timer() + ' Sorting completed')
else:
	inputBam = inBam

### ------------------------------------------------------------------------
### Generate sam file
### ------------------------------------------------------------------------

print( timer() + ' Generating SAM file')

comand3 = 'samtools view -h ' + inputBam + ' > ' + fileID + '.hisat2tophat.tmp.sam'
subprocess.call(comand3, shell = True)

print( timer() + ' SAM generation completed')

### ------------------------------------------------------------------------
### Parse file and write new lines
### ------------------------------------------------------------------------

print( timer() + ' Parsing SAM file')

## Open file handles
fh     = open(fileID + '.hisat2tophat.tmp.sam', 'r')
fh_out = open(fileID + '.edited.hisat2tophat.tmp.sam', 'w')

## create tracking objects
reads     = dict()
nRecords  = 0
nMapped   = 0

## Parse file and print new lines
for line in fh.readlines():

	# Print header
	if line[0] == '@':
		fh_out.write(line)

	# Parse alignment records
	else:
		line      = line.strip().split()
		flag      = int(line[1])
		nRecords +=1

		# Work only with mapped reads
		if is_mapped(flag):

			# GRab record information
			NH_line   = [match for match in line if 'NH:i:' in match][0]
			NH	  = int(NH_line.split(':')[-1])
			nMapped  +=1

			if NH > 1:

				# Obtain read id and pair
				sufix     = which_pair(flag)
				id        = line[0] + which_pair(flag)

				# Grab HI and update dictionary
				HI        = reads.get(id, (NH,0))[1]
				reads[id] = (NH, HI+1)

				# Errase key in dictionary if read is completed
				if reads[id][0] == reads[id][1]:
					del(reads[id])

			# Assign HI = 0 if only one mapping
			else:
				HI = 0

			# Create new line
			new_HI = 'HI:i:'+ str(HI)
			line.append(new_HI)
			fh_out.write('\t'.join(line)+'\n')

## Close file handles
fh.close()
fh_out.close()

print( timer() + ' Parsing SAM file completed')
print( timer() + ' Generating new BAM file')

### ------------------------------------------------------------------------------
### Create bam file
### ------------------------------------------------------------------------------
comand4 = 'samtools view -O BAM ' + fileID + '.edited.hisat2tophat.tmp.sam > ' + outBam
subprocess.call(comand4, shell = True)

### ------------------------------------------------------------------------------
### Remove temporary files and report stats
### ------------------------------------------------------------------------------

subprocess.call('rm *hisat2tophat.tmp*', shell = True)

print( timer() + ' File transformation completed')
print( timer() + ' Number of records processed: ' + str(nRecords))
print( timer() + ' Number of records discarded (unmapped): ' + str(nRecords - nMapped))

