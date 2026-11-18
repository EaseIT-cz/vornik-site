import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_build():
    spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    return build


class SiteTests(unittest.TestCase):
    def test_generated_pages_are_current_and_fully_translated(self):
        build = load_build()
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

    def test_catalog_text_cannot_break_html_attributes(self):
        build = load_build()
        original_read = Path.read_text

        def read(path, *args, **kwargs):
            content = original_read(path, *args, **kwargs)
            if path == ROOT / 'locales/cs.json':
                catalog = json.loads(content)
                catalog['meta.title'] = 'Vornik "česky" <test> & další'
                return json.dumps(catalog)
            return content

        with patch.object(Path, 'read_text', read):
            rendered = build.render_pages()[ROOT / 'cs/index.html']
        self.assertIn('content="Vornik &quot;česky&quot; &lt;test&gt; &amp; další"', rendered)

    def test_catalogs_do_not_contain_partial_tags_or_attributes(self):
        for lang in ('en', 'cs'):
            catalog = json.loads((ROOT / f'locales/{lang}.json').read_text())
            for key, value in catalog.items():
                self.assertFalse(value.startswith(('aria-label=', 'title=')), key)
                # A terminal's "> " prompt is text, not a partial opening tag.
                self.assertFalse(value.startswith('>') and not value.startswith('> '), key)

    def test_render_validation_rejects_broken_markup(self):
        build = load_build()
        with self.assertRaises(ValueError):
            build.validate_html('<html><body><p><strong>broken</p></body></html>')


if __name__ == '__main__':
    unittest.main()
