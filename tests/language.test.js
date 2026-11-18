const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const source = readFileSync(require('node:path').join(__dirname, '../language.js'), 'utf8');

function visit({ path = '/', languages = ['en-US'], saved, blocked = false, search = '', hash = '' } = {}) {
  let redirect;
  let ready;
  const links = ['en', 'cs'].map(language => ({
    href: `https://vornik.io/${language}/`, dataset: { language },
    addEventListener(type, callback) { this.click = callback; },
  }));
  const storage = {
    getItem() { if (blocked) throw Error('blocked'); return saved; },
    setItem(key, value) { if (blocked) throw Error('blocked'); saved = value; },
  };
  const location = { pathname: path, search, hash, replace(value) { redirect = value; } };
  vm.runInNewContext(source, {
    URL, localStorage: storage, navigator: { languages, language: languages[0] },
    location,
    document: {
      addEventListener(type, callback) { ready = callback; },
      querySelectorAll() { return links; },
    },
  });
  ready();
  return { redirect, links, location, saved: () => saved };
}

test('matches regional Czech and respects ordered supported preferences', () => {
  assert.equal(visit({ languages: ['cs-CZ', 'en'] }).redirect, '/cs/');
  assert.equal(visit({ languages: ['de-DE', 'cs', 'en'] }).redirect, '/cs/');
  assert.equal(visit({ languages: ['en-GB', 'cs'] }).redirect, '/en/');
  assert.equal(visit({ languages: ['fr'] }).redirect, '/en/');
  assert.equal(visit({ languages: [] }).redirect, '/en/');
});
test('explicit language wins over browser; unsupported stored values are ignored', () => {
  assert.equal(visit({ saved: 'en', languages: ['cs'] }).redirect, '/en/');
  assert.equal(visit({ saved: 'cs', languages: ['en'] }).redirect, '/cs/');
  assert.equal(visit({ saved: 'bad', languages: ['cs'] }).redirect, '/cs/');
});
test('locale links never redirect, including when storage disagrees', () => {
  for (const path of ['/en/', '/cs/', '/en/index.html', '/cs/index.html', '/vornik/']) {
    assert.equal(visit({ path, saved: 'cs', languages: ['cs'] }).redirect, undefined);
  }
});
test('storage denial does not break detection or manual switching', () => {
  const page = visit({ blocked: true, languages: ['cs-CZ'] });
  assert.equal(page.redirect, '/cs/');
  assert.doesNotThrow(() => page.links[0].click({ button: 0 }));
});
test('redirect and switch preserve query and section; click remembers the choice', () => {
  const page = visit({ languages: ['cs'], search: '?source=mail', hash: '#install' });
  assert.equal(page.redirect, '/cs/?source=mail#install');
  assert.equal(page.links[0].href, 'https://vornik.io/en/?source=mail#install');
  page.links[0].click({ button: 0 });
  assert.equal(page.saved(), 'en');
  page.links[1].click({ button: 0, ctrlKey: true });
  assert.equal(page.saved(), 'en');
});
test('switch preserves a section visited after page load', () => {
  const page = visit({ path: '/cs/' });
  page.location.hash = '#use-cases';
  page.links[0].click({ button: 0 });
  assert.equal(page.links[0].href, 'https://vornik.io/en/#use-cases');
});
