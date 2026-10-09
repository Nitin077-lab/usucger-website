/* USUCGER — shared behaviour. No dependencies. */
(function () {
  'use strict';

  /* ---------- reveal on scroll ----------
     threshold MUST stay 0: a ratio-based threshold can never be reached by a
     block taller than ~12x the viewport (the by-laws column is ~10,000px), which
     left those pages permanently invisible. revealVisible() is the failsafe. */
  var rv = [].slice.call(document.querySelectorAll('.rv'));
  function reveal(el) { el.classList.add('show'); }
  function revealVisible() {
    rv.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) reveal(el);
    });
  }
  if ('IntersectionObserver' in window && rv.length) {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { reveal(e.target); ro.unobserve(e.target); } });
    }, { threshold: 0, rootMargin: '0px 0px -60px 0px' });
    rv.forEach(function (el) { ro.observe(el); });
    window.addEventListener('load', revealVisible);
    setTimeout(revealVisible, 1500);
  } else {
    rv.forEach(reveal);
  }

  /* ---------- sticky nav shadow + back to top ---------- */
  var nav = document.getElementById('nav');
  var btt = document.getElementById('btt');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (nav) nav.classList.toggle('raised', y > 24);
    if (btt) btt.classList.toggle('on', y > 480);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (btt) btt.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  /* ---------- mobile drawer ---------- */
  var drawer = document.getElementById('drawer');
  var toggle = document.getElementById('navToggle');
  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
  }
  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.remove('open');
    document.body.style.overflow = '';
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }
  if (toggle) toggle.addEventListener('click', openDrawer);
  if (drawer) {
    drawer.addEventListener('click', function (e) {
      if (e.target.matches('.drawer-scrim, .drawer-close') || e.target.closest('.drawer-links a') || e.target.closest('.drawer-cta a')) closeDrawer();
    });
    drawer.querySelectorAll('.drawer-group > button').forEach(function (b) {
      b.addEventListener('click', function () { b.parentElement.classList.toggle('open'); });
    });
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeDrawer(); });

  /* ---------- tabs ---------- */
  document.querySelectorAll('[data-tabs]').forEach(function (group) {
    var btns = group.querySelectorAll('.tab-btn');
    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.getAttribute('data-tab');
        btns.forEach(function (b) { b.classList.toggle('on', b === btn); b.setAttribute('aria-selected', b === btn); });
        group.parentElement.querySelectorAll('.tab-panel').forEach(function (p) {
          var on = p.getAttribute('data-panel') === id;
          p.classList.toggle('on', on);
          // a panel that was display:none never fired the observer — reveal it now
          if (on) p.querySelectorAll('.rv').forEach(reveal);
        });
      });
    });
  });

  /* ---------- animated counters ---------- */
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        co.unobserve(e.target);
        var el = e.target, target = parseInt(el.getAttribute('data-count'), 10), v = 0,
            step = Math.max(1, Math.ceil(target / 55));
        var iv = setInterval(function () {
          v = Math.min(v + step, target);
          el.textContent = v;
          if (v >= target) clearInterval(iv);
        }, 20);
      });
    }, { threshold: 0.35 });
    counters.forEach(function (c) { co.observe(c); });
  } else {
    counters.forEach(function (c) { c.textContent = c.getAttribute('data-count'); });
  }

  /* ---------- searchable + sortable data tables ---------- */
  window.buildDataTable = function (opts) {
    var mount = document.getElementById(opts.mount);
    if (!mount) return;
    var rows = opts.rows.slice();
    var cols = opts.columns;
    var sortCol = opts.defaultSort == null ? 0 : opts.defaultSort;
    var sortDir = 1;
    var q = '';

    var toolbar = document.createElement('div');
    toolbar.className = 'tbl-toolbar';
    toolbar.innerHTML =
      '<div class="tbl-search"><span class="si" aria-hidden="true">&#128269;</span>' +
      '<input type="search" placeholder="' + (opts.placeholder || 'Search…') + '" aria-label="' + (opts.placeholder || 'Search') + '"></div>' +
      '<div class="tbl-count"></div>';

    var wrap = document.createElement('div');
    wrap.className = 'table-wrap' + (opts.scroll === false ? '' : ' table-scroll');
    var table = document.createElement('table');
    table.className = 'gtable';
    var thead = document.createElement('thead');
    var htr = document.createElement('tr');
    cols.forEach(function (c, i) {
      var th = document.createElement('th');
      th.textContent = c.label;
      if (c.sortable !== false) {
        th.className = 'sortable';
        th.setAttribute('role', 'button');
        th.setAttribute('tabindex', '0');
        var sar = document.createElement('span');
        sar.className = 'sar';
        sar.textContent = '▲▼';
        th.appendChild(sar);
        var doSort = function () {
          if (sortCol === i) { sortDir = -sortDir; } else { sortCol = i; sortDir = 1; }
          render();
        };
        th.addEventListener('click', doSort);
        th.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); doSort(); } });
      }
      htr.appendChild(th);
    });
    thead.appendChild(htr);
    var tbody = document.createElement('tbody');
    table.appendChild(thead);
    table.appendChild(tbody);
    wrap.appendChild(table);
    mount.appendChild(toolbar);
    mount.appendChild(wrap);

    var input = toolbar.querySelector('input');
    var count = toolbar.querySelector('.tbl-count');
    input.addEventListener('input', function () { q = input.value.trim().toLowerCase(); render(); });

    function render() {
      var view = rows.filter(function (r) {
        if (!q) return true;
        return r.join(' ').toLowerCase().indexOf(q) !== -1;
      });
      view.sort(function (a, b) {
        var x = (a[sortCol] || '').toLowerCase(), y = (b[sortCol] || '').toLowerCase();
        return x < y ? -sortDir : x > y ? sortDir : 0;
      });
      tbody.innerHTML = '';
      if (!view.length) {
        var tr = document.createElement('tr');
        var td = document.createElement('td');
        td.colSpan = cols.length;
        td.className = 'tbl-empty';
        td.textContent = 'No matches for “' + input.value + '”.';
        tr.appendChild(td); tbody.appendChild(tr);
      } else {
        var frag = document.createDocumentFragment();
        view.forEach(function (r) {
          var tr = document.createElement('tr');
          cols.forEach(function (c, i) {
            var td = document.createElement('td');
            var val = r[i] || '';
            if (!val) { td.className = 'muted'; val = '—'; }
            td.textContent = val;
            tr.appendChild(td);
          });
          frag.appendChild(tr);
        });
        tbody.appendChild(frag);
      }
      htr.querySelectorAll('th').forEach(function (th, i) {
        th.classList.remove('asc', 'desc');
        if (i === sortCol) th.classList.add(sortDir === 1 ? 'asc' : 'desc');
      });
      count.textContent = view.length + ' of ' + rows.length + ' ' + (opts.noun || 'entries');
    }
    render();
  };

  /* ---------- year in footer ---------- */
  document.querySelectorAll('[data-now-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();

/* ==================================================================== live bits */
(function () {
  'use strict';
  var DAY = 86400000;
  function daysUntil(iso) {
    var d = new Date(iso + 'T23:59:59');
    return Math.ceil((d - new Date()) / DAY);
  }

  /* ---------- deadline countdowns (sidebar card + ticker + inline callouts) ---------- */
  var list = document.querySelector('#deadlines .dl-list');
  if (list) {
    var rows = [].slice.call(list.querySelectorAll('.dl-row'));
    rows.forEach(function (r) {
      var n = daysUntil(r.getAttribute('data-deadline'));
      var days = r.querySelector('.dl-days'), unit = r.querySelector('.dl-unit');
      r.dataset.days = n;
      if (n < 0) {
        r.classList.add('past');
        days.textContent = '✓'; unit.textContent = 'closed';
        var det = r.querySelector('.dl-detail'); if (det) det.textContent = r.getAttribute('data-closed') || det.textContent;
      } else if (n === 0) { days.textContent = 'today'; unit.textContent = ''; r.classList.add('soon'); }
      else { days.textContent = n; unit.textContent = n === 1 ? 'day' : 'days'; if (n <= 30) r.classList.add('soon'); }
    });
    rows.sort(function (a, b) {
      var x = +a.dataset.days, y = +b.dataset.days;
      if (x < 0 && y < 0) return y - x; if (x < 0) return 1; if (y < 0) return -1; return x - y;
    }).forEach(function (r) { list.appendChild(r); });
  }
  document.querySelectorAll('.notice-item[data-deadline]').forEach(function (el) {
    if (daysUntil(el.getAttribute('data-deadline')) < 0) {
      var sep = el.nextElementSibling; el.remove(); if (sep && sep.classList.contains('notice-sep')) sep.remove();
    }
  });
  document.querySelectorAll('[data-deadline][data-closed]:not(.dl-row):not(.notice-item)').forEach(function (el) {
    if (daysUntil(el.getAttribute('data-deadline')) < 0) el.innerHTML = el.getAttribute('data-closed');
  });

  /* ---------- member map (real boundaries) ---------- */
  var stage = document.querySelector('.map-stage');
  if (stage && window.USUCGER_MAP) {
    var M = window.USUCGER_MAP, title = document.getElementById('mpTitle'), sub = document.getElementById('mpSub'), body = document.getElementById('mpBody');
    var base = { t: title.textContent, s: sub.textContent, h: body.innerHTML }, locked = null;
    function esc(s) { return s.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
    function block(u, cls) {
      var open = u.m.length && u.m.length <= 6 ? ' open' : '';
      return '<details class="mp-uni ' + cls + '"' + open + '><summary><span class="n">' + esc(u.n) + '</span><span class="c">' + (u.m.length || '&ndash;') + '</span><span class="chev">&#9660;</span></summary>' +
        (u.m.length ? '<ul>' + u.m.map(function (m) { return '<li>' + esc(m) + '</li>'; }).join('') + '</ul>' : '<ul><li style="background:none;color:var(--muted-lt);padding-left:0">No individual members listed for the current cycle</li></ul>') + '</details>';
    }
    function show(st) {
      var d = M[st]; if (!d) return;
      var nu = d.unis.length;
      title.textContent = d.name;
      sub.textContent = d.n ? d.n + ' member' + (d.n === 1 ? '' : 's') + (nu ? ' \u00b7 ' + nu + ' member institution' + (nu === 1 ? '' : 's') : '') : 'No members yet';
      var h = '';
      if (nu) h += d.unis.map(function (u) { return block(u, ''); }).join('');
      if (d.other.length) h += '<div class="mp-sec">Other affiliations</div>' + d.other.map(function (u) { return block(u, 'other'); }).join('');
      if (!nu && !d.other.length) h = '<p class="mp-hint">No USUCGER members here yet. Know a geotechnical program in ' + esc(d.name) + '? <a href="membership.html">Membership is $75 per person for three years.</a></p>';
      body.innerHTML = h; body.scrollTop = 0;
    }
    function reset() { title.textContent = base.t; sub.textContent = base.s; body.innerHTML = base.h; }
    var targets = stage.querySelectorAll('.usmap .st, .map-chips .chip');
    targets.forEach(function (t) {
      t.addEventListener('mouseenter', function () { if (!locked) show(t.dataset.st); });
      t.addEventListener('focus', function () { if (!locked) show(t.dataset.st); });
      t.addEventListener('mouseleave', function () { if (!locked) reset(); });
      var pick = function () {
        if (locked === t) { locked = null; t.classList.remove('locked'); reset(); return; }
        if (locked) locked.classList.remove('locked');
        locked = t; t.classList.add('locked'); show(t.dataset.st);
      };
      t.addEventListener('click', pick);
      t.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); } });
    });
  }

  /* ---------- site search (Ctrl/⌘+K) ---------- */
  var box = document.getElementById('search'), input = document.getElementById('searchInput'), out = document.getElementById('searchResults');
  if (!box) return;
  var hint = out.innerHTML, sel = -1, items = [];
  function open() { box.hidden = false; document.body.style.overflow = 'hidden'; setTimeout(function () { input.focus(); input.select(); }, 20); }
  function close() { box.hidden = true; document.body.style.overflow = ''; }
  ['searchOpen', 'searchOpenM'].forEach(function (id) { var b = document.getElementById(id); if (b) b.addEventListener('click', open); });
  document.getElementById('searchClose').addEventListener('click', close);
  box.querySelector('.search-scrim').addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); box.hidden ? open() : close(); }
    else if (e.key === 'Escape' && !box.hidden) close();
    else if (!box.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      e.preventDefault(); if (!items.length) return;
      sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items.forEach(function (a, i) { a.classList.toggle('sel', i === sel); });
      items[sel].scrollIntoView({ block: 'nearest' });
    } else if (!box.hidden && e.key === 'Enter' && sel >= 0 && items[sel]) { items[sel].click(); }
  });
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(s, terms) {
    var t = esc(s);
    terms.forEach(function (w) { if (w.length > 1) t = t.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
    return t;
  }
  function run() {
    var q = input.value.trim().toLowerCase(), idx = window.USUCGER_INDEX || [];
    sel = -1; items = [];
    if (q.length < 2) { out.innerHTML = hint; return; }
    var terms = q.split(/\s+/).filter(Boolean);
    var scored = [];
    for (var i = 0; i < idx.length; i++) {
      var e = idx[i], tl = e.t.toLowerCase(), score = 0, ok = true;
      for (var j = 0; j < terms.length; j++) {
        var w = terms[j];
        if (tl.indexOf(w) === 0) score += 12; else if (tl.indexOf(w) !== -1) score += 8;
        else if (e.s.toLowerCase().indexOf(w) !== -1) score += 4;
        else if (e.k.indexOf(w) !== -1) score += 1;
        else { ok = false; break; }
      }
      if (ok) scored.push([score + (e.p ? 3 : 0) - (e.u.indexOf('#') > -1 ? 0.5 : 0) - (e.u === 'directory.html' || e.s.indexOf('Member university') === 0 ? 0.25 : 0), i]);
    }
    scored.sort(function (a, b) { return b[0] - a[0]; });
    if (!scored.length) { out.innerHTML = '<div class="search-hint">Nothing matches “' + esc(input.value) + '”. Try a shorter word.</div>'; return; }
    out.innerHTML = scored.slice(0, 14).map(function (p) {
      var e = idx[p[1]];
      return '<a class="search-item" href="' + e.u + '"><span class="si-t">' + mark(e.t, terms) + '</span><span class="si-s">' + mark(e.s, terms) + '</span></a>';
    }).join('');
    items = [].slice.call(out.querySelectorAll('.search-item'));
  }
  input.addEventListener('input', run);
})();
(function(){var k=document.querySelector('.nav-search kbd');if(k&&!/Mac|iPhone|iPad/.test(navigator.platform))k.textContent='Ctrl K';})();

/* ---- Theme picker (home page only, for Board review) ---------------------
   Lists every theme in theme.json; the choice is saved in this browser and
   applied on every page by the small script in <head>. ?theme=<key> also works. */
(function () {
  var data = window.USUCGER_THEMES;
  if (!data || !document.querySelector('.hero')) return;
  var root = document.documentElement;
  var light = data.list.filter(function (t) { return t.l; }).map(function (t) { return t.k; });
  function apply(k) {
    root.setAttribute('data-theme', k);
    root.setAttribute('data-band', light.indexOf(k) > -1 ? 'light' : 'dark');
    try { localStorage.setItem('usucger-theme', k); } catch (e) {}
    dot.style.background = byKey[k].c; dot.style.boxShadow = 'inset -6px 0 0 ' + byKey[k].a;
  }
  var byKey = {}; data.list.forEach(function (t) { byKey[t.k] = t; });
  var box = document.createElement('div');
  box.className = 'theme-picker';
  box.innerHTML = '<label for="themeSelect">Color theme <span>preview</span></label><div class="tp-row"><span class="tp-dot" aria-hidden="true"></span><select id="themeSelect"></select></div><button type="button" class="tp-reset">Reset to default</button>';
  var sel = box.querySelector('select'), dot = box.querySelector('.tp-dot');
  data.list.forEach(function (t) {
    var o = document.createElement('option');
    o.value = t.k; o.textContent = t.n.replace(' — ', ': ') + (t.k === data.default ? ' (current)' : '');
    sel.appendChild(o);
  });
  var cur = root.getAttribute('data-theme');
  sel.value = byKey[cur] ? cur : data.default;
  sel.addEventListener('change', function () { apply(sel.value); });
  box.querySelector('.tp-reset').addEventListener('click', function () { sel.value = data.default; apply(data.default); });
  document.body.appendChild(box);
  apply(sel.value);
})();
