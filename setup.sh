#!/usr/bin/env bash
function find_os_version()
{
  try_release=$(lsb_release -rs 2> /dev/null || echo 'not found')
  if [ "${try_release}" != 'not found' ]
  then
    echo $(echo "${try_release}" | cut -f1 -d.)
    return 0
  fi

  try_release=$(rpm -q --queryformat '%{RELEASE}' rpm 2> /dev/null || echo 'not found')
  if [ "${try_release}" != 'not found' ]
  then
    echo $(echo "${try_release}" | grep -o [[:digit:]]*\$)
    return 0
  fi

  try_release=$(cat /etc/redhat-release 2> /dev/null || echo 'not found')
  if [ "${try_release}" != 'not found' ]
  then
    echo $(echo "${try_release}" | grep -o '[[:digit:]]' | head -1)
    return 0
  else
    echo "Unable to find current OS version, aborting"
    return -1
  fi
}

OS_VERSION=centos7
os_ver=$(find_os_version)
if [ "${os_ver}" == "6" ]
then
  OS_VERSION=slc6
fi
export OS_VERSION

LCG_VERSION=LCG_95
LCG_ARCH=x86_64-${OS_VERSION}-gcc8-opt
export LCG_VERSION
export LCG_ARCH

PROJECT_NAME="cms-l1t-analysis"

if [ -n "${PROJECT_ROOT}" ] ; then
   old_projectbase=${PROJECT_ROOT}
fi

if [ "x${BASH_ARGV[0]}" = "x" ]; then
    if [ ! -f setup.sh ]; then
        echo ERROR: must "cd where/${PROJECT_NAME}/is" before calling ". setup.sh" for this version of bash!
        PROJECT_ROOT=; export PROJECT_ROOT
        return 1
    fi
    PROJECT_ROOT="$PWD"; export PROJECT_ROOT
else
    # get param to "."
    envscript=$(dirname ${BASH_ARGV[0]})
    PROJECT_ROOT=$(cd ${envscript};pwd); export PROJECT_ROOT
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

source bin/env.sh
