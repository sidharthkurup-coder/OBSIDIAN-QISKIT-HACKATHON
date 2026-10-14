const fs = require('fs');
const t = fs.readFileSync('index.html', 'utf-8');
const js = t.match(/<script>([\s\S]*?)<\/script>/)[1];

// Minimal DOM stub with cached elements/buttons so onclick handlers persist
const elements = {};
const qcache = {};
function canvasCtxStub() {
  return new Proxy({}, {
    get(t, p) { if (p in t) return t[p]; return () => {}; },
    set(t, p, v) { t[p] = v; return true; }
  });
}
function makeEl(id) {
  return { id, innerHTML: '', textContent: '', classList: { add(){}, remove(){} },
           addEventListener(){}, dataset: {}, getContext() { return canvasCtxStub(); },
           width: 480, height: 360 };
}
global.document = {
  getElementById(id) { if (!elements[id]) elements[id] = makeEl(id); return elements[id]; },
  querySelectorAll(sel) {
    if (!qcache[sel]) {
      const f = makeEl(sel);
      if (sel === '#expMode .tab') f.dataset.m = 'ablation';
      if (sel === '#expSel .tab') f.dataset.s = 'chain_compatible';
      if (sel === '#expG .tab') f.dataset.g = '1.0';
      qcache[sel] = f;
    }
    return [qcache[sel]];
  }
};

try {
  eval(js);
  console.log('[1] Initial load (main mode): OK, cards len =', elements['expCards'].innerHTML.length);
} catch (e) {
  console.log('[1] ERROR on initial load:', e.constructor.name + ':', e.message);
  console.log('    ', (e.stack || '').split('\n')[1]);
}

// Simulate clicking the Ablation mode button (its onclick was registered during eval)
try {
  const btn = qcache['#expMode .tab'];
  if (btn && typeof btn.onclick === 'function') {
    btn.onclick();
    console.log('[2] Switch to ablation mode: OK, cards len =', elements['expCards'].innerHTML.length);
  } else {
    console.log('[2] no onclick registered on mode button');
  }
} catch (e) {
  console.log('[2] ERROR switching to ablation:', e.constructor.name + ':', e.message);
  console.log('    ', (e.stack || '').split('\n')[1]);
  console.log('    --- ablation card HTML (if any) ---');
  console.log((elements['expCards'].innerHTML || '').slice(0, 400));
}
// show a snippet of rendered cards for visual verification
{
  const html = elements['expCards'].innerHTML;
  const vals = html.match(/<div class="v[^"]*">[^<]+<\/div><div class="k">[^<]+/g) || [];
  console.log('    rendered cards:', vals.length);
  vals.slice(0, 4).forEach(v => console.log('     ', v.replace(/<[^>]+>/g, ' | ')));
}

// Simulate clicking g=1.0 in ablation mode
try {
  const gb = qcache['#expG .tab'];
  if (gb && typeof gb.onclick === 'function') {
    gb.onclick();
    console.log('[3] g re-select: OK, cards len =', elements['expCards'].innerHTML.length);
  }
} catch (e) {
  console.log('[3] ERROR on g re-select:', e.constructor.name + ':', e.message);
  console.log('    ', (e.stack || '').split('\n')[1]);
}
