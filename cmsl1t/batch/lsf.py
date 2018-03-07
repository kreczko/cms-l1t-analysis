import logging
import os
import re
import subprocess
from textwrap import dedent

from .common import Batch, Status

logger = logging.getLogger(__name__)

__bjobs_status = dict(
    PEND=Status.PENDING,
    PROV=Status.RUNNING,
    PSUSP=Status.FAILED,
    RUN='The job is currently running.',
    USUSP=Status.FAILED,
    SSUSP=Status.FAILED,
    DONE=Status.FINISHED,
    EXIT=Status.FAILED,
    UNKWN=Status.UNKNOWN,
    WAIT=Status.PENDING,
    ZOMBI=Status.FAILED,
)


def submit(config_files, batch_directory, batch_log_dir, run_script):
    logger.info("Will submit {0} jobs using bsub".format(len(config_files)))

    job_group = "/CMS-L1T--"
    directory_name = os.path.basename(os.path.dirname(batch_directory))
    job_group += directory_name.replace("/", "--")

    results = []
    for i, cfg in enumerate(config_files):
        logger.info("submitting: " + cfg)
        results.append(
            dict(
                batch_id=__submit_one(cfg, run_script, job_group),
                batch=Batch.lsf,
                config_file=cfg,
                stderr_log=None,
                stdout_log=None,
                job_log=None,
                status=Status.CREATED,
            )
        )

    logger.info(
        "\tCheck job status using:\n\n\t\tbjobs -g {0}".format(job_group)
    )
    return results


def __submit_one(config, run_script, group=None):
    # Prepare the args
    args = ["bsub", "-q", "8nm"]
    if group:
        args += ["-g", group]
    if not os.environ.get("DEBUG", False):
        args += ["-eo", os.devnull, "-oo", os.devnull]
    command = ' '.join([run_script, config])
    args += [command]
    job_id = 0
    try:
        out = subprocess.check_output(args)
        job_id = _parse_bsub_output(out)
    except subprocess.CalledProcessError as e:
        msg = dedent("""\
            Error submitting to bsub.
            Output was:
                {e.output}

            Return code was:
            {e.returncode}""")
        logger.error(msg.format(e=e))
        return False
    finally:
        return False
    return job_id


def _parse_bsub_output(bsub_output):
    """
    Job <145417932> is submitted to default queue <8nm>.
    """
    job_id = re.search(r'\d+', bsub_output).group()
    job_id = int(job_id)
    return job_id


def get_status(batch_id):
    args = ['bjobs', str(batch_id)]
    bjobs_output = subprocess.check_output(args)
    job_id, status = _parse_bjobs_output(bjobs_output)
    if job_id != batch_id:
        msg = 'Checked job ID "{0}" but found "{1}" - something went wrong'.format(
            batch_id, job_id)
        logger.error(msg)
        return Status.UNKNOWN
    return status


def _parse_bjobs_output(bjobs_output):
    global __bjobs_status
    bjobs_output = bjobs_output.lstrip('\n')
    entries = re.split("\n+", bjobs_output)
    tokens = entries[1].split(' ')
    tokens = [t for t in tokens if t != '']

    job_id = tokens[0]
    status = tokens[2]
    return int(job_id), __bjobs_status[status]
