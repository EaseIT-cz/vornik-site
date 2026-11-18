/* Static locale pages also work without JavaScript. Only the neutral homepage
 * detects a language; a shared /en/ or /cs/ URL always keeps its own language. */
(function () {
  'use strict';
  var supported = ['en', 'cs'];
  var storageKey = 'vornik:language';
  var saved;
  try { saved = localStorage.getItem(storageKey); } catch (e) {}

  if (location.pathname === '/' || location.pathname === '/index.html') {
    var language = supported.indexOf(saved) !== -1 ? saved : null;
    var preferences = navigator.languages && navigator.languages.length
      ? navigator.languages : [navigator.language || 'en'];
    for (var i = 0; !language && i < preferences.length; i++) {
      var base = preferences[i].toLowerCase().split(/[-_]/)[0];
      if (supported.indexOf(base) !== -1) language = base;
    }
    location.replace('/' + (language || 'en') + '/' + location.search + location.hash);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-language]').forEach(function (link) {
      function updateTarget() {
        var target = new URL(link.href);
        target.search = location.search;
        target.hash = location.hash;
        link.href = target.href;
      }
      updateTarget();
      link.addEventListener('click', function (event) {
        updateTarget();
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        try { localStorage.setItem(storageKey, link.dataset.language); } catch (e) {}
      });
    });
  });
})();
