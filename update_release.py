import json
import os
import re


def update_readme(release):
    input_file = 'README.md'
    with open(input_file) as f:
        content = f.readlines()

    pattern = "v(\d+\.)?(\d+\.)?(\*|\d+)$"
    for i, line in enumerate(content):
        if 'Latest stable version' in line:
            line = re.sub(pattern, 'v' + release, line)
            content[i] = line
            break

    content = ''.join(content)
    with open(input_file, 'w+') as f:
        f.write(content)


def update_changelog(release):
    input_file = 'CHANGELOG.md'
    with open(input_file) as f:
        content = f.read()
    content = content.replace('Unreleased', 'v' + release)
    content = content.replace('HEAD', 'v' + release)
    with open(input_file, 'w+') as f:
        f.write(content)


def update_package_version(release):
    input_file = 'cmsl1t/__init__.py'
    with open(input_file) as f:
        content = f.readlines()

    for i, line in enumerate(content):
        pattern = "(\d+\.)?(\d+\.)?(\*|\d+)"
        if '__version__' in line:
            line = re.sub(pattern, 'v' + release, line)
            content[i] = line
            break

    content = ''.join(content)
    with open(input_file, 'w+') as f:
        f.write(content)


def append_histoical_log():
    input_file = 'CHANGELOG.md'
    with open(input_file) as f:
        content = f.readlines()
    historical_changelog = 'docs/initial_changelog.md'
    with open(historical_changelog) as f:
        historical_content = f.readlines()

    content.insert(-2, ''.join(historical_content))
    content = ''.join(content)
    with open(input_file, 'w+') as f:
        f.write(content)

if __name__ == '__main__':
    release = os.environ.get('RELEASE', 'unreleased')
    update_readme(release)
    update_changelog(release)
    update_package_version(release)
    append_histoical_log()
