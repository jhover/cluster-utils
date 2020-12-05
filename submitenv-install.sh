#!/bin/bash -l
#
#  For job submission 
#
#
set -x

# Conda
conda install -c conda-forge mamba
mamba create -c conda-forge -c bioconda -n snakemake snakemake python=3.7

sleep 5

conda activate snakemake
sleep 5

# Conda available packages
conda install -y -c conda-forge -c bioconda snakemake drmaa
