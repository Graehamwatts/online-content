"""Validate dispatch values as data before writing the Actions environment file."""
import datetime
import os
import re


def resolve(env):
    if env.get('GITHUB_EVENT_NAME') == 'workflow_dispatch':
        mode = env.get('INPUT_MODE', '')
        target = env.get('INPUT_FORCE_TARGET', '')
        dry = env.get('INPUT_DRY_RUN', 'false')
        if mode not in {'remind', 'generate', 'watchdog'}:
            raise ValueError('Invalid mode')
        if dry not in {'true', 'false'}:
            raise ValueError('Invalid dry_run')
        if target:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', target):
                raise ValueError('Invalid target format')
            datetime.date.fromisoformat(target)
    else:
        mode = 'watchdog' if env.get('EVENT_SCHEDULE') == '23 16 * * *' else 'remind'
        target, dry = '', 'false'
    return {'MODE': mode, 'FORCE_TARGET': target, 'DRY_RUN': '1' if dry == 'true' else '0'}


if __name__ == '__main__':
    values = resolve(os.environ)
    values['GITHUB_RUN_URL'] = (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
                                f"/actions/runs/{os.environ['GITHUB_RUN_ID']}")
    with open(os.environ['GITHUB_ENV'], 'a') as output:
        for key, value in values.items():
            output.write(f'{key}={value}\n')
