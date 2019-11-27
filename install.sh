#! /usr/bin/env bash
module load python/anaconda-4.7.12
export PATH=/mnt/home/users/pab_001_uma/pedro/.local/bin:$PATH
pip install --user virtualenv
virtualenv safepy_env
source safepy_env/bin/activate
pip install ipykernel
pip install networkx
pip install pandas
pip install statsmodels
pip install matplotlib
pip install scipy
pip install tqdm
pip install numpy
pip install xlrd

pip install jupyterlab
# see extras/requirements.txt
ipython kernel install --user --name=safepy_env

