#! /usr/bin/env bash
module load python/anaconda-4.7.12
module load pandoc/2.2.1
export PATH=~pedro/.local/bin:$PATH
source safepy_env/bin/activate
jupyter nbconvert --to html /mnt/home/users/pab_001_uma/pedro/proyectos/netanalyzer/kernels/computeKernels/python/Power-Method.ipynb
