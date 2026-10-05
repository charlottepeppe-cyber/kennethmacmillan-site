// Mobile nav
const toggle = document.querySelector('.nav-toggle');
if (toggle) {
  const nav = document.getElementById('nav');
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
}

// Ballet catalogue: search + facet filters, reflected in the URL
const list = document.querySelector('[data-works]');
if (list) {
  const items = [...list.children];
  const search = document.querySelector('.search');
  const selects = [...document.querySelectorAll('select[data-filter]')];
  const count = document.querySelector('[data-count]');
  const empty = document.querySelector('[data-empty]');

  const params = new URLSearchParams(location.search);
  selects.forEach(s => {
    const v = params.get(s.dataset.filter);
    if (v) s.value = v;
  });
  if (params.get('q')) search.value = params.get('q');

  function apply(push) {
    const q = search.value.trim().toLowerCase();
    const active = selects
      .filter(s => s.value)
      .map(s => [s.dataset.filter, s.value]);

    let shown = 0;
    for (const li of items) {
      let ok = !q || li.dataset.search.includes(q);
      if (ok) {
        for (const [k, v] of active) {
          const field = li.dataset[k] || '';
          if (k === 'composer' || k === 'designer') {
            if (!field.split('|').includes(v)) { ok = false; break; }
          } else if (field !== v) { ok = false; break; }
        }
      }
      li.hidden = !ok;
      if (ok) shown++;
    }

    count.textContent = shown === items.length
      ? `${items.length} works`
      : `${shown} of ${items.length}`;
    empty.hidden = shown > 0;

    if (push) {
      const p = new URLSearchParams();
      if (q) p.set('q', q);
      active.forEach(([k, v]) => p.set(k, v));
      const qs = p.toString();
      history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
    }
  }

  search.addEventListener('input', () => apply(true));
  selects.forEach(s => s.addEventListener('change', () => apply(true)));
  apply(false);
}
