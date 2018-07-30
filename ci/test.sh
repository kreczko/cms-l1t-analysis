#!/usr/bin/env bash
export PATH=~/.local/bin:$PATH

cd ${CODE_PATH}
source bin/env.sh
make setup
ls -l build

if [ "x${CI_RUN_TEST}"== "xUNIT" ]
then
  make test
fi

if [ "x${CI_RUN_TEST}"== "xINTEGRATION" ]
then
  ./ci/integration-test.sh
fi
