import os
from textwrap import dedent

from .common import Status, Batch

from .condor import submit as condor_submit
from .condor import get_status as condor_status
from .lsf import submit as lsf_submit
from .lsf import get_status as lsf_status


def get_run_script(setup_script, shared_fs=True):
    project_root = os.environ["PROJECT_ROOT"]
    run_script_contents = [
        '#!/usr/bin/env bash',
        'pushd {project_root}',
        'source {setup_script}',
        'popd',
        'cmsl1t -c "$1"',
        '',
    ]
    if not shared_fs:
        # infer project root
        pass
    run_script_contents = '\n'.join(run_script_contents)
    run_script_contents = run_script_contents.format(
        project_root=project_root,
        setup_script=setup_script,
    )
    return run_script_contents


def prepare_input_file_groups(input_ntuples, files_per_job):
    file_lists = []
    current_list = []
    for infile in input_ntuples:
        if not infile.startswith("root:"):
            infile = os.path.realpath(infile)
        current_list.append(infile)

        # Is the current list full?
        if len(current_list) >= files_per_job:
            file_lists.append(current_list)
            current_list = []

    # Even if the last list had fewer files than needed, make sure to use this
    # too
    if current_list:
        file_lists.append(current_list)

    return file_lists


__all__ = [
    'Status',
    'Batch',
    'condor_submit',
    'condor_status',
    'get_run_script',
    'prepare_input_file_groups',
    'lsf_submit',
    'lsf_status',
]
