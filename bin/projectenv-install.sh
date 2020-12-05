#!/bin/bash -l
#  For project1 template. 
set -x

# Conda
conda create -y -n projectenv python=3.7
sleep 5

conda activate projectenv
sleep 5

# Conda available packages
conda install -y pandas numpy scipy seaborn matplotlib plotly h5py 
conda install -y pyarrow nltk bottleneck  # for ben's egad code
conda install -y tzlocal # for rpy2

# Standard pip packages
pip install tables pyreadr mglearn  sklearn  pdpipe  pyuniprot  dendropy  pronto

# Git via pip
# pip install git+https://github.com/Parsl/parsl.git

# Tarball installs
wget ftp://emboss.open-bio.org/pub/EMBOSS/EMBOSS-6.6.0.tar.gz
tar -xvzf EMBOSS-6.6.0.tar.gz
cd EMBOSS-6.6.0
./configure --without-x --prefix=$CONDA_PREFIX
make
make install 
cd ..
rm -rf EMBOSS-6.6.0 EMBOSS-6.6.0.tar.gz