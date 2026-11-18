# Vornik site: instructions for maintainers and agents

This repository is the static website at vornik.io, not the Vornik daemon or
documentation website. Read [the maintenance guide](docs/maintaining-the-site.md)
before changing the landing page.

## Edit sources, generate pages

- Shared page layout, CSS and inline application JS: `templates/index.html`.
- English content: `locales/en.json`. Czech content: `locales/cs.json`.
- Browser detection and language-switch persistence: `language.js`.
- Generator, supported languages and Open Graph locale mapping: `scripts/build.py`.
- Generated output: `index.html`, `en/index.html`, `cs/index.html`.

Never edit generated HTML directly. After editing a template, any catalog,
or generator behavior, run `python3 scripts/build.py`. Commit source and all
changed generated pages together. Do not run the generator to modify the
independent Go module discovery pages under `vornik/`.

Before committing any website change, run:

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests
node --test tests/*.test.js
git diff --check
```

Use a local HTTP server to check both `/en/` and `/cs/` after visible or
behavioral changes. Check mobile layout and translated install/copy controls.
For language navigation changes, also check a Czech browser preference at `/`,
manual choice persistence, direct locale links, and JavaScript disabled.

Do not change user-facing commands, endpoint URLs, Go import metadata, or
machine status names just to translate them. Community and Enterprise are
edition names. Translate human-facing content and accessibility labels.
Keep catalog key sets identical. Plain tokens are escaped; only reviewed
markup uses `|html`, and JavaScript values use `|json`.

## Coordinate with other maintainers

Use a feature branch and review changes before merging. Compare with the latest
base branch before handoff; if shared template/catalog changes conflict, resolve
the source conflicts first and regenerate HTML. Do not resolve generated-page
conflicts independently. Check the diff for accidental edits and unrelated work.

Shared RAG notes about this site may use `repo_scope: "*"` (the scope visible
across repositories) so agents working from other repositories can find them;
label them with
`github.com/EaseIT-cz/vornik-site` and date them. Verify notes against these
files. Update RAG when maintenance behavior changes; never record credentials.
State whether changes are local, pushed, or merged. Do not claim deployment
from a local commit or companion review.
