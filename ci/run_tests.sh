#!/usr/bin/env bash
# set -x
source bin/env.sh
export PATH=~/.local/bin:$PATH
make setup
ls -l build
make test
