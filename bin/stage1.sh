#!/bin/bash 
#   Usage: runsamtools <setup> <infile> <outfile>
#
#   args = $(setup) 
#          $(basefile)
#          $(outdir)
#          			$(outdir)/$(filebase).Aligned.out.bam  
#          			$(outdir)/$(filebase).Aligned.sortedByCoord.out.bam
#   request_cpus = 10
#   request_memory = 20480
#
# job name
#$ -N run4sam
#
# job indexes for array all jobs, but only run 10 at a time for disk quota 
#$ -t 1-357 -tc 4
#
# processes per job
#$ -pe threads 20
#
#$ -wd /grid/gillis/data/hover/work/werner1/
#
# Per-thread memory request. 
#$ -l m_mem_free=2G



