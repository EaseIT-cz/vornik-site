# Vornik website

Static website for vornik.io. No runtime framework or dependencies required.

## Languages

- `/en/` is English; `/cs/` is Czech. Both pages work without JavaScript.
- `/` uses the visitor's saved language choice, then the first supported
  language in the browser's preferences, with English as the fallback.
- The EN / CZ buttons remember an explicit choice in local storage. Direct
  locale URLs always display their language, regardless of that preference.
- Section anchors and query parameters survive language changes. Without
  JavaScript, the root page displays English and the language links still work.

Edit `templates/index.html` for shared layout and `locales/en.json` /
`locales/cs.json` for content. Catalog values can include trusted inline HTML;
`{{key|json}}` safely encodes values used in JavaScript. Keep all catalog keys
in sync. Language codes and locale metadata live in `scripts/build.py`, the
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
