import logging
import os
import subprocess
from textwrap import dedent

from .common import Status

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

def submit(config_files, batch_directory, run_script):
    logger.info("Will submit {0} jobs using bsub".format(len(config_files)))

    job_group = "/CMS-L1T--"
    directory_name = os.path.basename(os.path.dirname(batch_directory))
    job_group += directory_name.replace("/", "--")

    results = []
    for i, cfg in enumerate(config_files):
        logger.info("submitting: " + cfg)
        results.append(__submit_one(cfg, run_script, job_group))

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

    try:
        subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        msg = dedent("""\
            Error submitting to bsub.
            Output was:
                {e.output}

            Return code was:
            {e.returncode}""")
        logger.error(msg.format(e=e))
        return False
    return True


def get_status(batch_id):
    args = ['bjobs', str(batch_id)]
    bjobs_output = subprocess.check_output(args)
    job_id, status = __parse_bjobs_output(bjobs_output)
    if job_id != batch_id:
        msg = 'Checked job ID "{0}" but found "{1}" - something went wrong'.format(
            batch_id, job_id)
        logger.error(msg)
        return Status.UNKNOWN
    return status


def __parse_bjobs_output(bjobs_output):
    bjobs_output = bjobs_output.lstrip('\n')
    entries = re.split("\n+", bjobs_output)
    tokens = entries[1].split(' ')
    tokens = [t for t in tokens if t != '']

    job_id = tokens[0]
    status = tokens[2]
    return int(job_id), bjobs_status[status]
