#!/usr/bin/env python3
"""Render static locale pages with Python's standard library only."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\{\{([\w.]+)(\|json)?\}\}')
LANGUAGES = {'en': 'en_US', 'cs': 'cs_CZ'}


def render_pages():
    template = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
    catalogs = {
        lang: json.loads((ROOT / f'locales/{lang}.json').read_text(encoding='utf-8'))
        for lang in LANGUAGES
    }
    keys = set(catalogs['en'])
    pages = {}
    for lang, catalog in catalogs.items():
        if set(catalog) != keys or not all(isinstance(v, str) and v for v in catalog.values()):
            raise ValueError(f'{lang}: missing, extra, or empty translations')
        values = {
            **catalog,
            'lang': lang,
            'ogLocale': LANGUAGES[lang],
            **{f'current.{code}': ' aria-current="page"' if code == lang else ''
               for code in LANGUAGES},
        }

        def substitute(match):
            value = values[match[1]]
            # Catalogs are reviewed source, and may contain inline HTML.
            # JSON encoding prevents translated quotes breaking JavaScript.
            return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c') if match[2] else value

        rendered = TOKEN.sub(substitute, template)
        if '{{' in rendered:
            raise ValueError(f'{lang}: unresolved template token')
        pages[ROOT / lang / 'index.html'] = rendered
        if lang == 'en':
            # English fallback for no-JS visitors; language.js selects a locale
            # before rendering on a normal browser's visit to the root URL.
            pages[ROOT / 'index.html'] = rendered
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if generated pages are stale')
    args = parser.parse_args()
    for path, content in render_pages().items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                raise SystemExit(f'{path.relative_to(ROOT)} is stale; run python3 scripts/build.py')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
