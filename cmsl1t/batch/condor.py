import htcondor
import logging
import os
import socket
import re

from .common import Status, Batch
from plumbum import local

logger = logging.getLogger(__name__)

CONDOR_STATUS = [
    Status.CREATED,
    Status.PENDING,
    Status.RUNNING,
    Status.FINISHED,
    Status.HELD,
]


def submit(config_files, batch_directory, batch_log_dir, run_script):
    logger.info("Will submit {0} jobs".format(len(config_files)))
    schedd = htcondor.Schedd()
    results = []
    with schedd.transaction() as txn:
        for i, cfg in enumerate(config_files):
            result = __submit_one(
                txn, i, cfg, batch_directory, batch_log_dir, run_script
            )
            results.append(result)

    return results


def __submit_one(txn, index, config_file, batch_directory, batch_log_dir, run_script):
    cfg = os.path.realpath(config_file)
    stderr_log = os.path.join(batch_log_dir, 'job_{0}.err'.format(index))
    stdout_log = os.path.join(batch_log_dir, 'job_{0}.out'.format(index))
    job_log = os.path.join(batch_log_dir, 'job_{0}.log'.format(index))
    job_cfg = dict(
        executable=run_script,
        arguments="-c {}".format(cfg),
        output=stdout_log,
        error=stderr_log,
        log=job_log,
    )
    out = None
    if 'cern.ch' in socket.gethostname():
        out = _submit_one_console(job_cfg, batch_log_dir)
    else:
        sub = htcondor.Submit(job_cfg)
        out = sub.queue(txn)
    return dict(
        batch_id=int(out),
        batch=Batch.condor,
        config_file=cfg,
        stderr_log=stderr_log,
        stdout_log=stdout_log,
        job_log=job_log,
        status=Status.CREATED,
    )


def _submit_one_console(job_cfg, batch_log_dir):
    condor_submit_file = os.path.join(batch_log_dir, 'job_{0}.submit'.format(index))
    with open(condor_submit_file, 'w') as f:
        content = '\n'.join([k + ' = ' + v for k, v in job_cfg.items()])
        content += 'queue' + '\n'
        f.write(content)
    condor_submit = local('condor_submit')
    out = condor_submit[condor_submit_file]
    return __parse_condor_submit_output(out)


def __parse_condor_submit_output(out):
    m = re.search(r"(submitted to cluster) (\d+)\.", out)
    return int(m.group(2))


def get_status(batch_id):
    schedd = htcondor.Schedd()
    status, exit_code = __status_from_schedd(batch_id, schedd)
    if status == Status.UNKNOWN:
        from_history = __status_from_history(batch_id, schedd)
        if from_history is None:
            return Status.UNKNOWN
        status, exit_code = from_history

    if exit_code is None or exit_code == 0:
        return status
    else:
        return Status.FAILED


def __status_from_schedd(batch_id, schedd):
    query = schedd.query('ClusterId=={0:d}'.format(
        batch_id), ['JobStatus', 'ExitCode'])
    if not query or query is None:
        return Status.UNKNOWN, None
    for job in query:
        exit_code = job['ExitCode'] if 'ExitCode' in job else None
        status = CONDOR_STATUS[job['JobStatus']]
        return status, exit_code


def __status_from_history(batch_id, schedd):
    query = 'ClusterId=={0:d}'.format(batch_id)
    for job in schedd.history(query, ['JobStatus', 'ExitCode'], 1):
        exit_code = job['ExitCode'] if 'ExitCode' in job else None
        status = CONDOR_STATUS[job['JobStatus']]
        return status, exit_code


def resubmit(config_files, local_ids, batch_directory, batch_log_dir, run_script):
    logger.info("Will resubmit {0} jobs".format(len(config_files)))
    schedd = htcondor.Schedd()
    results = []
    with schedd.transaction() as txn:
        for i, cfg in zip(local_ids, config_files):
            result = __submit_one(
                txn, i, cfg, batch_directory, batch_log_dir, run_script
            )
            results.append(result)

    return results
