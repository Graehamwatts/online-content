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
                self.assertEqual(job['environment'], 'service-automation')
                for step in job['steps']:
                    self.assertNotIn('${{', step.get('run', ''), str(path))
                    if 'uses' in step:
                        self.assertRegex(step['uses'], r'@[0-9a-f]{40}$')

if __name__ == '__main__':
    unittest.main()
