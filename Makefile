# simple makefile to simplify repetitive build env management tasks under posix

PYTHON := $(shell which python)

all: clean setup

clean-build:
	@rm -fr build

clean-external:
	@rm -fr external

clean-so:
	@[ -d external ] && find external -name "*.so" -exec rm {} \;
	@find legacy -name "*.so" -exec rm {} \;

clean-pyc:
	@find . -name "*.pyc" -exec rm {} \;

clean: clean-build clean-so clean-pyc clean-external


# setup
setup: setup-build-dir setup-external setup-data-dir


setup-external:
	@./bin/get_l1Analysis
	@./bin/compile_l1Analysis

setup-build-dir:
	@mkdir -p build

create-data-dir:
		@mkdir -p data

setup-data-dir: create-data-dir data/L1Ntuple_test_1.root data/L1Ntuple_test_2.root data/L1Ntuple_test_3.root

data/L1Ntuple_test_1.root:
	@xrdcp root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/bundocka/cmsl1t/test_0.root ./data/L1Ntuple_test_1.root || true

data/L1Ntuple_test_2.root:
	@xrdcp root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/bundocka/cmsl1t/test_1.root ./data/L1Ntuple_test_2.root || true

data/L1Ntuple_test_3.root:
	@xrdcp root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/bundocka/cmsl1t/test_2.root ./data/L1Ntuple_test_3.root || true


# tests
pep8:
	@pep8 --exclude=.git,external examples cmsl1t

flake8:
	@flake8 $(shell file -p bin/* |awk -F: '/python.*text/{print $$1}') cmsl1t test --ignore=F401 --max-line-length=120

# benchmarks
NTUPLE_CFG := "legacy/Config/ntuple_cfg.h"
benchmark: clean-benchmark setup-benchmark run-benchmark

clean-benchmark:
		@rm -fr benchmark

setup-benchmark:
ifeq ($(wildcard benchmark),)
	@mkdir -p benchmark/legacy
	@mkdir -p benchmark/current
endif

run-benchmark:
	@time python -m memory_profiler bin/run_benchmark

test: test-code flake8

test-all: test-code-full flake8

test-code:
	@pytest -v -m "not xrootdtest" test

test-code-full:
	@pytest -v test

changelog:
	@github_changelog_generator -u cms-l1t-offline -p cms-l1t-analysis

docs-html:
	cd docs; make html; cd -

docs-latex:
	cd docs; make latexpdf; cd -

release: changelog update_release

update_release:
	@python update_release.py
	@echo "Check everything and if OK, execute"
	@echo "git add -u"
	@echo "git commit -m 'tagged version ${RELEASE}'"
	@echo "git push upstream master"
	@echo "git tag v${RELEASE}"
	@echo "git push upstream v${RELEASE}"
