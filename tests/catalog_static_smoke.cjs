// Deterministic DOM stub, not a browser or visual-acceptance test.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const dataText = fs.readFileSync(path.join(root, 'data/catalog_manifest.json'), 'utf8');
const data = JSON.parse(dataText);
const template = fs.readFileSync(path.join(root, 'templates/unified_catalog.html'), 'utf8');
const script = template.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements = new Map();
function get(id) {
  if (!elements.has(id)) elements.set(id, {
    innerHTML: '', textContent: id === 'catalog-data' ? dataText : '', value: 'any',
    style: {}, classList: { toggle() {}, remove() {}, add() {} }, scrollIntoView() {},
  });
  return elements.get(id);
}
const context = {
  document: { getElementById: get, querySelectorAll: () => [] }, Intl,
  fetch() { throw Error('Network forbidden in static catalog'); },
  localStorage: new Proxy({}, { get() { throw Error('Storage forbidden'); } }),
};
vm.createContext(context);
vm.runInContext(script, context);
assert.equal(vm.runInContext('state.mode', context), 'explore');
assert.ok(get('visibleCount').textContent.startsWith(`${data.repositories.length} unique repositories`));
assert.equal((get('nav').innerHTML.match(/class="navitem"/g) || []).length, data.categories.length);
const rendered = get('categories').innerHTML;
for (const repo of data.repositories) assert.ok(rendered.includes(`href="${repo.url}"`), repo.fullName);
assert.ok(!rendered.includes('Loading'));
vm.runInContext('state.q="Game Engines";renderAll()', context);
for (const repo of data.repositories.filter(r => r.primaryCategory === 'game_engines')) {
  assert.ok(get('categories').innerHTML.includes(`href="${repo.url}"`), repo.fullName);
}
vm.runInContext('state.q="gohugoio/hugo";renderAll()', context);
assert.ok(get('visibleCount').textContent.startsWith('1 unique repositories'));
assert.ok(get('categories').innerHTML.includes('href="https://github.com/gohugoio/hugo"'));
console.log(`PASS: ${data.repositories.length} startup records; ${data.categories.length} navigation nodes; static rendering and label/name search; no network/storage. DOM stub only.`);
