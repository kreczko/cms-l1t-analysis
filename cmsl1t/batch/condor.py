import htcondor
import logging
import os
from textwrap import dedent

from .common import Status

logger = logging.getLogger(__name__)


def submit(config_files, batch_directory, run_script):
    logger.info("Will submit {0} jobs".format(len(config_files)))
    schedd = htcondor.Schedd()
    results = []
    for cfg in config_files:
        with schedd.transaction() as txn:
            cfg = os.path.realpath(cfg)
            job_cfg = dict(executable=run_script,
                           arguments="-c {}".format(cfg),
                           )
            sub = htcondor.Submit(job_cfg)
            out = sub.queue(txn)
            results.append(out)
    logger.info(dedent("""\
    Jobs should be running on htcondor now.  To monitor their progress use:

        condor_q $USER """))

    return results


def get_status(batch_id):
    raise NotImplementedError('condor.get_status is not implemented (yet)')
    return Status.UNKNOWN
