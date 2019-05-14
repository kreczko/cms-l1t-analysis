#!/usr/bin/env bash
if test -e ${CMSL1T_CONDA_PATH} ; then
    echo "Miniconda already installed."
else
  echo "Installing miniconda."
  rm -rf ${CMSL1T_CONDA_PATH}
  mkdir -p $HOME/download
  if [[ -d $HOME/download/miniconda.sh ]] ; then rm -rf $HOME/download/miniconda.sh ; fi
  wget -c https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh -O $HOME/download/miniconda.sh
  chmod +x $HOME/download/miniconda.sh
  $HOME/download/miniconda.sh -b -p ${CMSL1T_CONDA_PATH}
fi
