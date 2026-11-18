# Maintaining vornik.io

This guide applies to `github.com/EaseIT-cz/vornik-site`. It is intended for
people and coding agents sharing the site and its RAG context.

## What build.py does

`scripts/build.py` is a development-time generator using Python 3's standard
library. It reads the shared `templates/index.html` and the language catalogs
in `locales/`, then writes these deployable pages:

| Output | Purpose |
| --- | --- |
| `index.html` | English fallback at `/`; JavaScript selects the visitor's locale. |
| `en/index.html` | English page at `/en/`. |
| `cs/index.html` | Czech page at `/cs/`. |

The generator checks catalog key parity, nonempty strings, unresolved tokens
and balanced HTML tags. `--check` verifies that the committed output matches
the sources without writing files. It reports failure if any generated page
is missing or stale. Balanced tags are a limited structural check, not a full
HTML validator or sanitizer; reviewed rich markup still requires care.

The public website never runs Python. These generated pages are committed and
served directly by the repository's existing static hosting. Merging a PR
with the regenerated pages needs no Python installation, server-side build,
dependency installation, or new hosting configuration. Publishing still
depends on the repository's normal hosting workflow; a local commit alone
does not deploy anything.

## When to run the generator

| Change | Run `python3 scripts/build.py`? |
| --- | --- |
| Copy, headings, navigation labels, metadata or accessibility text in a catalog | Yes. Update both catalogs as needed. |
| Shared HTML, inline CSS, inline JS or language links in `templates/index.html` | Yes. |
| Generator logic, supported languages or Open Graph locale mapping in `scripts/build.py` | Yes. |
| Add or remove a language | Yes, after updating every language registry and link. |
| Resolve a template/catalog merge conflict | Yes, after resolving source files. |
| Only `language.js`, `brand-tokens.css`, fonts, icons or other independent assets | No, unless the template or catalogs also change. Test the behavior/assets. |
| Only README, AGENTS.md, this guide, or tests | No, unless the documented change also changes a generation input. Run the checks. |
| Go module discovery pages under `vornik/` | No. They are separate hand-maintained pages. |
| Generated HTML was accidentally edited directly | Discard that edit by regenerating; move any intended change into its source. |

Run commands from the repository root. A shell with Python 3 is sufficient
for generation; Node.js is additionally needed for the JavaScript tests.

## Normal edit and review workflow

1. Read `AGENTS.md`, inspect `git status`, and work on a feature branch.
   Confirm the base branch and any concurrent edits before starting.
2. Edit the source template or catalogs. For a new content key, add it to
   every catalog in the same change. Do not hand-edit generated output.
3. Run `python3 scripts/build.py` when the table above requires it.
4. Run the checks:

   ```sh
   python3 scripts/build.py --check
   python3 -m unittest discover -s tests
   node --test tests/language.test.js
   git diff --check
   ```

5. For visible or behavioral edits, preview with
   `python3 -m http.server 8000`. Check `http://localhost:8000/en/` and
   `http://localhost:8000/cs/` on desktop and mobile. Check install mode
   switching and copy labels in both the hero and final widget.
6. For locale changes, test `/` with Czech and English browser preferences,
   a saved manual choice, direct locale URLs, query/section preservation,
   unavailable local storage and JavaScript disabled. The first visit's
   locale is selected from a saved choice, then ordered supported browser
   languages, then English. Only `/` and `/index.html` redirect.
7. Review the source diff and regenerated pages, commit them together, and
   submit or update the PR. If source conflicts arise, resolve the source
   first, regenerate all pages, then rerun checks. Do not hand-merge generated
   HTML separately. Inspect the final diff before staging.
8. Update shared RAG if the structure or maintenance procedure changed.
   Identify this repository, date, branch/commit and whether it is merged.
   A companion review supplies findings; verify them before changing code.

## Translation contexts

`{{key}}` escapes text and quoted attributes. Keep tags and attribute syntax
in the template. `{{key|html}}` inserts explicitly reviewed inline markup;
`{{key|json}}` encodes a JavaScript value and prevents a translated string
from closing its surrounding script tag. These filters are not interchangeable.
Catalogs are trusted, reviewed repository source, never visitor input.

Translate prose, accessibility labels and copy feedback. Keep technical
commands, URLs, machine statuses and product/edition names intact. In
particular, `Community` and `Enterprise` identify editions. The shell command
must stay executable and identical between locales; the natural-language
agent installation prompt is translated.

## Adding a language

1. Copy `locales/en.json` to the new language-code filename, translate every
   value and retain the exact key set.
2. Add its language code and Open Graph locale to `LANGUAGES` in
   `scripts/build.py`; this creates `<code>/index.html` during generation.
3. Add the code to `supported` in `language.js` in the same change.
4. Add its native-language switch link, `hreflang` alternate, and active-link
   placeholder to `templates/index.html`. Active-link placeholders use the
   `current.<code>|html` convention. Keep English as the fallback unless the
   product's default is deliberately changed.
5. Expand tests to include the new locale, its regional browser preference,
   metadata, switch control and explicit choice. Regenerate, preview and
   commit the new generated page along with the updated existing pages.
6. Update the language list in README and this guide, then refresh shared RAG.

## Hosting and language behavior

Direct `/en/` and `/cs/` URLs always retain their own language. EN/CZ clicks
save an explicit preference in browser local storage when available. With
JavaScript, navigation retains the query string and current section. Without
JavaScript, the root remains English and language links open the target
locale's homepage; they cannot preserve the current query/section or save a
preference. The root's canonical points at `/en/` because its static fallback
content duplicates English; `x-default` points at `/` for language selection.

Assets and language links use root-relative URLs for vornik.io. Do not deploy
this site under an arbitrary URL subdirectory without revisiting those paths.
The Go import discovery metadata at `/vornik/` and `/vornik/enterprise/` is
independent of landing-page translations and must be preserved.
