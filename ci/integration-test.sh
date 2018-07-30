#!/usr/bin/env bash

configs='all2017 demo efficiencies gen offline_met_studies rates rateVsPU study_tower298_met weekly_checks'

for c in $configs
do
  cmsl1t -c config/$c.yaml
done
