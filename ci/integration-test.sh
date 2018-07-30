#!/usr/bin/env bash

# configs='all2017 demo efficiencies gen offline_met_studies rates rateVsPU study_tower28_met weekly_checks'
configs='all2017 demo efficiencies offline_met_studies rates rateVsPU study_tower28_met weekly_checks'
configs='rates rateVsPU study_tower28_met weekly_checks'

for c in $configs
do
  set -x
  cmsl1t -c config/$c.yaml
  set +x
done
