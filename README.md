# Vornik website

Static website for vornik.io. No runtime framework or dependencies required.

## Languages

- `/en/` is English; `/cs/` is Czech. Both pages work without JavaScript.
- `/` uses the visitor's saved language choice, then the first supported
  language in the browser's preferences, with English as the fallback.
- The EN / CZ buttons remember an explicit choice in local storage. Direct
  locale URLs always display their language, regardless of that preference.
- With JavaScript enabled, section anchors and query parameters survive
  language changes. Without JavaScript, the root page displays English and
  the language links open the selected locale's homepage.

Edit `templates/index.html` for shared layout and `locales/en.json` /
`locales/cs.json` for content. Text is HTML-escaped by default;
`{{key|html}}` allows reviewed inline markup and `{{key|json}}` safely encodes
values used in JavaScript. Tags and attributes belong in the template, not
in translated labels. Generation rejects unbalanced HTML. Community and
Enterprise are edition names and remain unchanged in both languages.
Keep all catalog keys in sync. Language codes and locale metadata live in
`scripts/build.py`, the
switcher and alternate links in the template, and detection in `language.js`.
To add a language, update those three files and add its complete catalog.

Generate the pages and run checks with Python 3 and Node.js:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests
node --test tests/*.test.js
```

Commit generated `index.html`, `en/index.html`, and `cs/index.html` together
with source changes: hosting serves them directly, with no build step.
The `/vornik/` and `/vornik/enterprise/` paths contain Go module discovery
metadata and are independent of the translated landing pages.

For a local preview: `python3 -m http.server 8000`.

## Maintenance by people and agents

Start with [AGENTS.md](AGENTS.md) and the detailed
[maintenance guide](docs/maintaining-the-site.md). The committed files are the
source of truth; RAG supplies shared context and must be checked against the
current checkout. The guide lists exactly which edits require generation,
how to add a language, the review checks, and what merging deploys.
