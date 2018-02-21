import htcondor
import logging
import os

from .common import Status, Batch

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
            cfg = os.path.realpath(cfg)
            stderr_log = os.path.join(batch_log_dir, 'job_{0}.err'.format(i))
            stdout_log = os.path.join(batch_log_dir, 'job_{0}.out'.format(i))
            job_log = os.path.join(batch_log_dir, 'job_{0}.log'.format(i))
            job_cfg = dict(
                executable=run_script,
                arguments="-c {}".format(cfg),
                output=stdout_log,
                error=stderr_log,
                log=job_log,
            )
            sub = htcondor.Submit(job_cfg)
            out = sub.queue(txn)
            results.append(
                dict(
                    batch_id=int(out),
                    batch=Batch.condor,
                    config_file=cfg,
                    stderr_log=stderr_log,
                    stdout_log=stdout_log,
                    job_log=job_log,
                    status=Status.CREATED,
                )
            )

    return results


def get_status(batch_id):
    schedd = htcondor.Schedd()
    status, exit_code = __status_from_schedd(batch_id, schedd)
    if status == Status.UNKNOWN:
        status, exit_code = __status_from_history(batch_id, schedd)

    if exit_code is None or exit_code == 0:
        return status
    else:
        return Status.FAILED


def __status_from_schedd(batch_id, schedd):
    job = schedd.query('ClusterId==38', ['JobStatus', 'ExitCode'])
    if job:
        exit_code = job['ExitCode'] if 'ExitCode' in job else None
        return job['JobStatus'], exit_code
    else:
        return Status.UNKNOWN, None


def __status_from_history(batch_id, schedd):
    query = 'ClusterId=={0}'.format(batch_id)
    for job in schedd.history(query, ['JobStatus', 'ExitCode'], 1):
        exit_code = job['ExitCode'] if 'ExitCode' in job else None
        return job['JobStatus'], exit_code
