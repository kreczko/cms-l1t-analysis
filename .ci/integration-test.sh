#!/usr/bin/env bash
set -e
set -x
cmsl1t -c config/${CI_RUN_CONFIG}.yaml
set +x
set +e
