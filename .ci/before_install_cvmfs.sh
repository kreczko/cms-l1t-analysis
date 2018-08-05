#!/usr/bin/env bash

if test -e /cvmfs ; then
    echo "CVMFS already installed."
else
    echo "Installing CVMFS."
    mkdir -p $HOME/download
    if [[ -d $HOME/download/cvmfs-release-latest_all.deb ]] ; then rm -rf $HOME/download/cvmfs-release-latest_all.deb ; fi
    wget --no-check-certificate https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb -O $HOME/download/cvmfs-release-latest_all.deb
    sudo dpkg -i cvmfs-release-latest_all.deb

    sudo apt-get update
    sudo apt-get install cvmfs cvmfs-config-default
    rm -f cvmfs-release-latest_all.deb

    if [[ -d $HOME/download/default.local ]] ; then rm -rf $HOME/download/default.local ; fi
    wget --no-check-certificate https://lcd-data.web.cern.ch/lcd-data/CernVM/default.local -O $HOME/download/default.local
    sudo mkdir -p /etc/cvmfs
    sudo cp -p $HOME/download/default.local /etc/cvmfs/default.local
    sudo /etc/init.d/autofs stop
    sudo mkdir -p /cvmfs/grid.cern.ch /cvmfs/sft.cern.ch
    sudo mount -t cvmfs grid.cern.ch /cvmfs/grid.cern.ch
    sudo mount -t cvmfs sft.cern.ch /cvmfs/sft.cern.ch
    ls /cvmfs/grid.cern.ch
    ls /cvmfs/sft.cern.ch
fi


wget --no-check-certificate https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb
sudo dpkg -i cvmfs-release-latest_all.deb
sudo apt-get update
sudo apt-get install cvmfs cvmfs-config-default
rm -f cvmfs-release-latest_all.deb
wget --no-check-certificate https://lcd-data.web.cern.ch/lcd-data/CernVM/default.local
sudo mkdir -p /etc/cvmfs
sudo mv default.local /etc/cvmfs/default.local
sudo /etc/init.d/autofs stop
sudo cvmfs_config setup
sudo mkdir -p /cvmfs/clicdp.cern.ch
sudo mount -t cvmfs clicdp.cern.ch /cvmfs/clicdp.cern.ch
ls /cvmfs/clicdp.cern.ch
