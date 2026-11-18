import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_generated_pages_are_current_and_fully_translated(self):
        spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        for path, content in build.render_pages().items():
            self.assertEqual(path.read_text(), content, f'Rebuild {path}')
            self.assertNotIn('{{', content)
        en = json.loads((ROOT / 'locales/en.json').read_text())
        cs = json.loads((ROOT / 'locales/cs.json').read_text())
        self.assertEqual(en.keys(), cs.keys())
        self.assertTrue(all(cs.values()))

    def test_localized_pages_include_metadata_and_working_controls(self):
        for lang in ('en', 'cs'):
            html = (ROOT / lang / 'index.html').read_text()
            self.assertIn(f'<html lang="{lang}">', html)
            self.assertIn(f'rel="canonical" href="https://vornik.io/{lang}/"', html)
            self.assertIn('hreflang="cs" href="https://vornik.io/cs/"', html)
            self.assertIn('hreflang="en" href="https://vornik.io/en/"', html)
            self.assertIn(f'data-language="{lang}" aria-current="page"', html)
            self.assertEqual(html.count('data-install>'), 2)
            self.assertIn('curl -fsSL https://get.vornik.io | bash', html)
        czech = (ROOT / 'cs/index.html').read_text()
        self.assertIn('Kopírovat příkaz', czech)
        self.assertIn('Zkopírováno', czech)
        self.assertIn('Dokumentace', czech)


if __name__ == '__main__':
    unittest.main()
