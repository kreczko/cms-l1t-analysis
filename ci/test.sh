#!/usr/bin/env bash
export PATH=~/.local/bin:$PATH

cd ${CODE_PATH}
source bin/env.sh
make setup
ls -l build
make test
