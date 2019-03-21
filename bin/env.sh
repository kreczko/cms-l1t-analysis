#!/bin/bash
PROJECT_NAME="cms-l1t-analysis"

if [ -n "${PROJECT_ROOT}" ] ; then
   old_projectbase=${PROJECT_ROOT}
fi

if [ "x${BASH_ARGV[0]}" = "x" ]; then
    if [ ! -f bin/env.sh ]; then
        echo ERROR: must "cd where/${PROJECT_NAME}/is" before calling ". bin/env.sh" for this version of bash!
        PROJECT_ROOT=; export PROJECT_ROOT
        return 1
    fi
    PROJECT_ROOT="$PWD"; export PROJECT_ROOT
else
    # get param to "."
    envscript=$(dirname ${BASH_ARGV[0]})
    PROJECT_ROOT=$(cd ${envscript}/..;pwd); export PROJECT_ROOT
fi

# clean PATH and PYTHONPATH
if [ -n "${old_projectbase}" ] ; then
  PATH=`python ${PROJECT_ROOT}/bin/remove_from_path.py "$PATH" "${old_projectbase}"`
  PYTHONPATH=`python ${PROJECT_ROOT}/bin/remove_from_path.py "$PYTHONPATH" "${old_projectbase}"`
fi

# add project to PYTHONPATH
if [ -z "${PYTHONPATH}" ]; then
   PYTHONPATH=${PROJECT_ROOT}; export PYTHONPATH
else
   PYTHONPATH=${PROJECT_ROOT}:$PYTHONPATH; export PYTHONPATH
fi

# add project to PATH
PATH=${PROJECT_ROOT}/bin:$PATH; export PATH
# add local bin to PATH (for local flake8 installations, etc)
export PATH=~/.local/bin:$PATH

unset old_projectbase
unset envscript

if [[ -z "${NO_CVMFS}" ]]
then
  echo "Getting dependencies from CVMFS"
  # this gives you voms-proxy-*, xrdcp and other grid tools
  source /cvmfs/grid.cern.ch/etc/profile.d/setup-cvmfs-ui.sh
  # ROOT 6, voms-proxy-init and other things
  source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc62-opt/setup.sh
  # to fix java for the hadoop commands:
  unset JAVA_HOME
  pip install --user -r requirements.txt
else
  echo "No CVMFS available, setting up Anaconda Python"
  if [ ! -d "${CMSL1T_CONDA_PATH}" ]
  then
    wget -nv https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p ${CMSL1T_CONDA_PATH}
    PATH=${CMSL1T_CONDA_PATH}/bin:$PATH; export PATH
    rm -f miniconda.sh
    echo "Finished conda installation, creating new conda environment"
    conda config --add channels http://conda.anaconda.org/NLeSC
    conda config --set show_channel_urls yes
    conda create -n cms python=2.7 -yq
    source activate cms
    conda install -y -q \
      matplotlib \
      numpy \
      root>=6.04 \
      rootpy
    echo "Created conda environment, installing basic dependencies"
    pip install -U pip
    pip install -r requirements.txt
    conda clean -t -y
  fi
  source activate cms
fi

# Capture the user's site-packages directory:
USER_SITE_PACKAGES="$(python -c "import site; print(site.USER_SITE)")"
# add project to PYTHONPATH
PYTHONPATH="${USER_SITE_PACKAGES}:$PYTHONPATH"

git submodule init
git submodule update

ulimit -c 0

echo "Environment for ${PROJECT_NAME} is ready"
