const fs = require('fs');

// stubs before loading md.js
global.window = { MD_URL: 'README.md' };
global.document = { readyState: 'complete', getElementById: () => null, addEventListener() {}, title: '' };

const mdjs = fs.readFileSync('md.js', 'utf-8');
eval(mdjs);
const render = window.__md.renderMarkdown;
const inline = window.__md.inline;

let fails = 0;
function check(name, cond, extra) {
  if (cond) console.log('  PASS:', name);
  else { fails++; console.log('  FAIL:', name, extra || ''); }
}

console.log('=== README.md render ===');
try {
  const readme = fs.readFileSync('README.md', 'utf-8');
  const h = render(readme);
  check('has <h1>', /<h1>/.test(h));
  check('has <h2> sections', (h.match(/<h2>/g) || []).length >= 5, (h.match(/<h2>/g) || []).length);
  check('has table', h.includes('<table>') && h.includes('</table>'));
  check('has th cells', h.includes('<th>'));
  check('has code', h.includes('<code>'));
  check('has strong', h.includes('<strong>'));
  check('has hr', h.includes('<hr>'));
  check('ablation img linked', h.includes('<img src="results/ablation.png"'));
  check('escaped pipe restored in table cell', h.includes('|E_noisy − E_exact|'));
  check('list rendered', h.includes('<li>'));
  console.log('  rendered bytes:', h.length);
} catch (e) { fails++; console.log('  EXCEPTION:', e.message); }

console.log('=== results/RESULTS.md render ===');
try {
  const res = fs.readFileSync('results/RESULTS.md', 'utf-8');
  const h = render(res);
  check('has table', h.includes('<table>'));
  check('5 data sections', (h.match(/<h2>/g) || []).length >= 5, (h.match(/<h2>/g) || []).length);
  check('escaped |E−E_exact| cell renders', h.includes('|E−E_exact|'));
  check('all tables column-consistent', (() => {
    const tables = h.match(/<table>[\s\S]*?<\/table>/g) || [];
    if (tables.length < 1) return false;
    for (const tbl of tables) {
      const ncols = (tbl.match(/<th>/g) || []).length;
      if (ncols === 0) return false;
      const rows = tbl.match(/<tr>[\s\S]*?<\/tr>/g) || [];
      for (const r of rows) {
        const tds = (r.match(/<td>/g) || []).length;
        if (tds !== 0 && tds !== ncols) {
          console.log('    mismatch: header', ncols, 'body', tds);
          return false;
        }
      }
    }
    return true;
  })());
  check('some table has 8 columns (§3 noisy results)', (() => {
    const tables = h.match(/<table>[\s\S]*?<\/table>/g) || [];
    return tables.some(t => (t.match(/<th>/g) || []).length === 8);
  })());
  check('noise row has value 0.2547', h.includes('0.2547'));
  console.log('  rendered bytes:', h.length);
} catch (e) { fails++; console.log('  EXCEPTION:', e.message); }

console.log('=== link rewriting ===');
check('README.md link -> readme.html', inline('[doc](README.md)').includes('href="readme.html"'));
check('results/RESULTS.md link -> results.html', inline('[res](results/RESULTS.md)').includes('href="results.html"'));
check('normal link untouched', inline('[x](https://example.com)').includes('href="https://example.com"'));
check('inline code protected', inline('use `a * b` here').includes('<code>a * b</code>'));
check('bold works', inline('**bold**').includes('<strong>bold</strong>'));

console.log(fails === 0 ? '\nALL TESTS PASSED' : `\n${fails} FAILURES`);
process.exit(fails === 0 ? 0 : 1);
