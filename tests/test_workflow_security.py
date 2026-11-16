import importlib.util
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('resolver', ROOT / 'scripts/resolve_postcard_inputs.py')
resolver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolver)

class SecurityTests(unittest.TestCase):
    def test_dispatch_validation(self):
        base = {'GITHUB_EVENT_NAME': 'workflow_dispatch', 'INPUT_MODE': 'remind',
                'INPUT_FORCE_TARGET': '2026-11-24', 'INPUT_DRY_RUN': 'true'}
        self.assertEqual(resolver.resolve(base), {'MODE': 'remind', 'FORCE_TARGET': '2026-11-24', 'DRY_RUN': '1'})
        for key, bad in [('INPUT_MODE', '$(touch /tmp/pwned)'), ('INPUT_MODE', 'remind\nEVIL=1'),
                         ('INPUT_FORCE_TARGET', '2026-11-24"; touch /tmp/pwned; #'),
                         ('INPUT_FORCE_TARGET', '2026-11-24\nEVIL=1'),
                         ('INPUT_FORCE_TARGET', '`id`'), ('INPUT_FORCE_TARGET', '2026-02-30'),
                         ('INPUT_DRY_RUN', 'true\nEVIL=1')]:
            with self.subTest(key=key, value=bad), self.assertRaises(ValueError):
                resolver.resolve({**base, key: bad})

    def test_schedule(self):
        self.assertEqual(resolver.resolve({'EVENT_SCHEDULE': '23 16 * * *'})['MODE'], 'watchdog')
        self.assertEqual(resolver.resolve({})['MODE'], 'remind')

    def test_workflow_boundaries(self):
        import re
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            data = yaml.safe_load(path.read_text())
            self.assertEqual(data['permissions'], {'contents': 'read'})
            for job in data['jobs'].values():
                scheduled = 'schedule' in data['on']
                expected = "${{ github.event_name == 'schedule' && 'service-automation-scheduled' || 'service-automation' }}" if scheduled else 'service-automation'
                self.assertEqual(job['environment'], expected)
                self.assertIn("github.ref == 'refs/heads/main'", job['if'])
                self.assertIn("github.actor == 'Graehamwatts'", job['if'])
                self.assertIn("github.triggering_actor == 'Graehamwatts'", job['if'])
                for step in job['steps']:
                    self.assertNotIn('${{', step.get('run', ''), str(path))
                    if 'uses' in step:
                        self.assertRegex(step['uses'], r'@[0-9a-f]{40}$')

    def test_public_markers_do_not_store_addresses(self):
        import datetime, json, tempfile
        from unittest.mock import patch
        def load(name):
            spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        reminder = load('postcard_preview_reminder')
        generator = load('postcard_preview_generate')
        fake = ['one@example.invalid', 'two@example.invalid']
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(reminder, 'STATE_DIR', directory):
                drop = datetime.date(2026, 11, 24)
                reminder.write_marker(drop, fake)
                text = Path(reminder.marker_path(drop)).read_text()
                self.assertEqual(json.loads(text)['recipient_count'], 2)
                for address in fake:
                    self.assertNotIn(address, text)
                self.assertNotIn('recipients', json.loads(text))
            generated = Path(directory) / 'generated.json'
            generator.write_sent_marker(generated, '2026-11-24', 2, ['synthetic-A'])
            self.assertEqual(json.loads(generated.read_text())['recipient_count'], 2)
            self.assertNotIn('recipients', json.loads(generated.read_text()))

    def test_early_validation_failure_keeps_run_link(self):
        import os, subprocess, tempfile
        workflow = yaml.safe_load((ROOT / '.github/workflows/farming-postcard-reminder.yml').read_text())
        failure = next(step for step in workflow['jobs']['postcard-preview']['steps']
                       if step.get('name') == 'Open issue on failure')
        self.assertEqual(failure['env']['GITHUB_RUN_URL'],
                         '${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}')
        with tempfile.TemporaryDirectory() as directory:
            env = {'PATH': os.environ['PATH'], 'GITHUB_ENV': str(Path(directory) / 'env'),
                   'GITHUB_EVENT_NAME': 'workflow_dispatch', 'INPUT_MODE': 'bad',
                   'GITHUB_RUN_URL': 'https://github.com/example/test/actions/runs/123'}
            result = subprocess.run(['python3', str(ROOT / 'scripts/resolve_postcard_inputs.py')],
                                    env=env, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(Path(env['GITHUB_ENV']).exists())
            # A fake gh emits arguments only: no GitHub issue or network request.
            fake_gh = Path(directory) / 'gh'
            fake_gh.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            fake_gh.chmod(0o700)
            env['PATH'] = directory + os.pathsep + env['PATH']
            body = subprocess.check_output(['bash', '-eu', '-c', failure['run']], env=env, text=True)
            self.assertIn('Run: ' + env['GITHUB_RUN_URL'], body)
        self.assertIn('github.event_name', workflow['concurrency']['group'])

    def test_retired_templates_are_inert(self):
        for name in ['archive/morning-command-center/morning-command-center.yml',
                     'runbooks/friday-attribution-review-workflow.yml',
                     'runbooks/daily-attribution-brief-workflow.yml']:
            self.assertEqual(yaml.safe_load((ROOT / name).read_text()), {})

    def test_no_recipient_fields_in_script_serializers(self):
        import ast
        # Includes retired scripts. Email transport may use recipients; persisted
        # dictionaries must not contain that field.
        paths = list((ROOT / 'scripts').glob('*.py')) + list((ROOT / '.github/scripts').glob('*.py'))
        paths += list((ROOT / 'archive').rglob('*.py'))
        for path in paths:
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    self.assertFalse(any(isinstance(key, ast.Constant) and key.value == 'recipients'
                                         for key in node.keys), str(path))

if __name__ == '__main__':
    unittest.main()
