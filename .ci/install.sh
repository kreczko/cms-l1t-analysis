#!/usr/bin/env bash
set -e
if test -e ${CMSL1T_CONDA_PATH}/envs/cms; then
    echo "cms env already exists."
else
    echo "Creating cms env."
    conda create --yes -q -n cms python=${TRAVIS_PYTHON_VERSION}
fi

source activate cms
conda install -y -q psutil

conda config --add channels http://conda.anaconda.org/NLeSC
conda config --set show_channel_urls yes

conda install -y -q \
  matplotlib \
  numpy \
  root>=6.04 \
  rootpy

pip install -U pip
pip install -r requirements.txt
source deactivate
set +e
