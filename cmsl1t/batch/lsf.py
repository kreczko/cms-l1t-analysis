import logging
import os
from textwrap import dedent


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
