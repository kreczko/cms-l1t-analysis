from textwrap import dedent


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
