import os
from textwrap import dedent

from .common import Batch, create_run_script, create_info_file, \
    get_config_name_template, prepare_jobs, prepare_output_folders, Status

from .condor import submit as condor_submit
from .condor import get_status as condor_status
from .condor import resubmit as condor_resubmit
from .lsf import submit as lsf_submit
from .lsf import get_status as lsf_status


__all__ = [
    'Batch',
    'condor_resubmit',
    'condor_status',
    'condor_submit',
    'create_info_file',
    'create_run_script',
    'get_config_name_template',
    'prepare_jobs',
    'prepare_output_folders',
    'Status',
    'lsf_status',
    'lsf_submit',
]
