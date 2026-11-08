(() => {
'use strict';
const DATA = window.OBJECTIVES || [];
const STORE = 'fifa27-companion-v1';
const SNAPSHOT = window.SNAPSHOT || '';
document.getElementById('stand').textContent = SNAPSHOT;

/* ---------- Zustand ---------- */
let state = { done: {}, cat: 'Alle', q: '', sort: 'expiry', hideDone: false };
try { const s = JSON.parse(localStorage.getItem(STORE) || 'null'); if (s && s.done) state = Object.assign(state, s); } catch (e) {}
const save = () => { try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) {} };
const key = (g, t) => g.id + ':' + t.n;
const isDone = (g, t) => !!state.done[key(g, t)];
const doneCount = g => g.tasks.filter(t => isDone(g, t)).length;

/* ---------- Helfer ---------- */
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const PERM_YEAR = 2030;
const endMs = g => Date.parse(g.ends);
const isPerm = g => new Date(g.ends).getUTCFullYear() >= PERM_YEAR;
const now = () => Date.now();
const alive = g => endMs(g) > now();

function left(g) {
  const ms = endMs(g) - now();
  if (ms <= 0) return { txt: 'Abgelaufen', cls: 'bad', ms };
  if (isPerm(g)) return { txt: 'Dauerhaft', cls: 'perm', ms };
  const m = Math.floor(ms / 60000), h = Math.floor(m / 60), d = Math.floor(h / 24);
  let txt;
  if (d >= 2) txt = `${d} Tage ${h % 24} Std`;
  else if (d === 1) txt = `1 Tag ${h % 24} Std`;
  else if (h >= 1) txt = `${h} Std ${m % 60} Min`;
  else txt = `${m} Min`;
  const cls = ms < 24 * 36e5 ? 'bad' : ms < 72 * 36e5 ? 'warn' : '';
  return { txt, cls, ms };
}
const fmtDate = iso => new Intl.DateTimeFormat('de-DE', { weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' }).format(new Date(iso));
const fmtShort = iso => new Intl.DateTimeFormat('de-DE', { weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(iso));
const fmtLong = iso => new Intl.DateTimeFormat('de-DE', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(iso));

/* ---------- Icons ---------- */
const SVG = {
  clock: '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 5v5.2l4 2.4-1 1.7-5-3V7h2Z"/></svg>',
  back: '<svg viewBox="0 0 24 24"><path d="M15.4 5.4 14 4l-8 8 8 8 1.4-1.4L8.8 12z"/></svg>',
  check: '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  coin: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#e9b200"/><circle cx="12" cy="12" r="8.6" fill="#ffd84a"/><path d="M12 6.5v11M9 9.2c0-1.2 1.3-2 3-2s3 .8 3 2-1.3 1.7-3 2.1-3 .9-3 2.1 1.3 2 3 2 3-.8 3-2" fill="none" stroke="#a66f00" stroke-width="1.6" stroke-linecap="round"/></svg>',
  bolt: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#7b2bff"/><path d="M13.5 3 6 13.5h5L10 21l8-11h-5.2z" fill="#fff"/></svg>',
  style: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#0fa3b8"/><path d="M12 4.5l6 2.2v4.6c0 3.7-2.4 6.6-6 8.2-3.6-1.6-6-4.5-6-8.2V6.7z" fill="#fff"/></svg>',
  key: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#2a8c5a"/><path d="M8.5 15.5a3.5 3.5 0 1 1 3.2-4.9H19v2.3h-1.5v1.8H15.6v-1.8h-3.9a3.5 3.5 0 0 1-3.2 2.6Zm0-2.3a1.2 1.2 0 1 0 0-2.4 1.2 1.2 0 0 0 0 2.4Z" fill="#fff"/></svg>',
  gift: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#c2306b"/><path d="M6.5 10h11v2h-11zM7.5 12.5h9V18h-9zM11 9.4 9.5 8a1.3 1.3 0 1 1 1.4-2.2c.8.3 1.1 1.6 1.1 3.6 0-2 .3-3.3 1.1-3.6A1.3 1.3 0 1 1 14.5 8L13 9.4z" fill="#fff"/></svg>',
  pack: '<svg viewBox="0 0 24 24"><defs><linearGradient id="gp" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffd84a"/><stop offset="1" stop-color="#e08a00"/></linearGradient></defs><path d="M7 2h10l2 3v15l-2 2H7l-2-2V5z" fill="url(#gp)"/><path d="M12 7.2l1.3 2.7 3 .4-2.2 2.1.5 3-2.6-1.4-2.6 1.4.5-3L7.7 10.3l3-.4z" fill="#fff" opacity=".9"/></svg>',
  pick: '<svg viewBox="0 0 24 24"><rect x="3" y="6" width="11" height="15" rx="1.5" fill="#2d6bff" transform="rotate(-12 8 13)"/><rect x="9" y="3" width="11" height="15" rx="1.5" fill="#ffd84a" transform="rotate(10 14 10)"/><path d="M14.5 7.5l1 2 2.2.3-1.6 1.5.4 2.2-2-1.1-2 1.1.4-2.2-1.6-1.5 2.2-.3z" fill="#7a4d00"/></svg>',
  season: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#0fb5c8"/><path d="M12 5l2 4.6 5 .5-3.8 3.3 1.1 4.9L12 15.8 7.7 18.3l1.1-4.9L5 10.1l5-.5z" fill="#fff"/></svg>',
  champ: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#7b2bff"/><path d="M8 6h8v4a4 4 0 0 1-8 0zM6 7h2v2a2 2 0 0 1-2-2zm12 0h-2v2a2 2 0 0 0 2-2zM11 14h2v3h2v2H9v-2h2z" fill="#fff"/></svg>',
  gallery: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#c2306b"/><rect x="6" y="7" width="12" height="10" rx="1" fill="none" stroke="#fff" stroke-width="2"/><path d="M7 16l3.5-4 2.5 3 2-2 2 3z" fill="#fff"/></svg>',
  token: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#2d6bff"/><circle cx="12" cy="12" r="7" fill="none" stroke="#fff" stroke-width="2"/><circle cx="12" cy="12" r="2.6" fill="#fff"/></svg>'
};
const svgIco = (k, cls = 'ico') => `<span class="${cls} ico-svg">${SVG[k]}</span>`;

function kindIcon(r, cls = 'ico') {
  switch (r.kind) {
    case 'coins': return svgIco('coin', cls);
    case 'pack': return svgIco('pack', cls);
    case 'pick': return svgIco('pick', cls);
    case 'season': return svgIco('season', cls);
    case 'champtoken': return svgIco('champ', cls);
    case 'gallerytoken': return svgIco('gallery', cls);
    case 'boost': return svgIco('bolt', cls);
    case 'style': return svgIco('style', cls);
    case 'access': return svgIco('key', cls);
    default: return svgIco('gift', cls);
  }
}
const kindText = r => r.kind === 'style' ? `Chemie-Stil: ${r.text}` : r.text;

const SIL = '<svg class="pc-sil" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="34" r="19"/><path d="M12 100c0-24 17-38 38-38s38 14 38 38z"/></svg>';
function playerCard(r, cls = '') {
  const c = r.col || {};
  const st = (r.stats || []).map(s => `<span><b>${esc(s[1])}</b>${esc(s[0])}</span>`).join('');
  return `<div class="pc ${cls}" style="--hd:${c.header || '#fff'};--c1:${c['chip-bg'] || '#1d2d57'}" title="${esc(r.name)} · ${esc((r.pos || []).join(', '))}">
    ${SIL}<div class="pc-rate">${esc(r.rating)}</div><div class="pc-pos">${esc((r.pos || [])[0] || '')}</div>
    <div class="pc-name">${esc(r.name)}</div><div class="pc-st">${st}</div></div>`;
}
const chip = (r, big = false) => `<span class="rw ${big ? 'big' : ''}">${kindIcon(r)}<span>${esc(kindText(r))}</span></span>`;

/* ---------- Übersicht ---------- */
const CATS = ['Alle', 'Kampagnen', 'Saison', 'FC Pro', 'Grundlagen', 'Meilensteine', 'Meisterschaft'];

function matches(g) {
  if (state.cat !== 'Alle' && g.cat !== state.cat) return false;
  const q = state.q.trim().toLowerCase();
  if (q) {
    const hay = [g.title, g.desc, ...g.rewards.map(r => r.text || r.name),
      ...g.tasks.flatMap(t => [t.title, t.desc, ...t.rewards.map(r => r.text || r.name)])].join(' ').toLowerCase();
    if (!q.split(/\s+/).every(w => hay.includes(w))) return false;
  }
  if (state.hideDone && doneCount(g) === g.tasks.length) return false;
  return true;
}
const sorters = {
  expiry: (a, b) => endMs(a) - endMs(b) || a.title.localeCompare(b.title, 'de'),
  progress: (a, b) => (doneCount(b) / b.tasks.length) - (doneCount(a) / a.tasks.length) || endMs(a) - endMs(b),
  name: (a, b) => a.title.localeCompare(b.title, 'de')
};

function heroArt(g) {
  const p = g.rewards.find(r => r.kind === 'player');
  if (p) return playerCard(p, 'sm');
  const r = g.rewards[0];
  return r ? kindIcon(r, 'ico-xl') : '';
}

function card(g) {
  const dc = doneCount(g), n = g.tasks.length, all = dc === n;
  const L = left(g);
  const pct = Math.round(dc / n * 100);
  const rws = g.rewards.filter(r => r.kind !== 'player');
  const shown = rws.slice(0, 3).map(r => chip(r)).join('');
  const more = rws.length > 3 ? `<span class="rw more">+${rws.length - 3}</span>` : '';
  return `<button class="card ${all ? 'done' : ''}" data-id="${g.id}" data-cat="${esc(g.cat)}" type="button">
    <div class="c-top"><span class="tag">${esc(g.cat)}</span>
      <span class="timer ${L.cls}">${SVG.clock}<span data-timer="${g.id}">${L.txt}</span></span></div>
    <div class="c-main"><div class="c-text"><h3 class="c-title">${esc(g.title)}</h3><p class="c-desc">${esc(g.desc)}</p></div>
      <div class="c-art">${heroArt(g)}</div></div>
    <div class="c-foot"><div class="c-meta"><span>${dc} / ${n} Aufgaben</span><span>${pct}%</span></div>
      <div class="bar"><i style="width:${pct}%"></i></div>
      <div class="rw-row">${shown}${more}</div></div>
    ${all ? '<span class="stamp">Erledigt</span>' : ''}</button>`;
}

function render() {
  const live = DATA.filter(alive);
  // Chips
  $('#chips').innerHTML = CATS.map(c => {
    const n = live.filter(g => c === 'Alle' || g.cat === c).length;
    return `<button class="chip" role="tab" aria-selected="${state.cat === c}" data-cat="${esc(c)}">${esc(c)}<small>${n}</small></button>`;
  }).join('');
  // Hero + Kopf
  const tasksAll = live.flatMap(g => g.tasks.map(t => [g, t]));
  const doneAll = tasksAll.filter(([g, t]) => isDone(g, t)).length;
  const pct = tasksAll.length ? Math.round(doneAll / tasksAll.length * 100) : 0;
  const soon = live.filter(g => !isPerm(g) && endMs(g) - now() < 72 * 36e5 && doneCount(g) < g.tasks.length).length;
  const open = tasksAll.length - doneAll;
  const groupsDone = live.filter(g => doneCount(g) === g.tasks.length).length;
  const C = 2 * Math.PI * 54;
  $('#hero').innerHTML = `
    <div class="ring"><svg viewBox="0 0 132 132"><defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#2ee6ff"/><stop offset="1" stop-color="#d4ff3a"/></linearGradient></defs>
      <circle class="tr" cx="66" cy="66" r="54" fill="none" stroke-width="12"/>
      <circle class="pg" cx="66" cy="66" r="54" fill="none" stroke-width="12" stroke-linecap="butt" stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - pct / 100)}"/></svg>
      <div class="ring-c"><div><b>${pct}%</b><br><small>geschafft</small></div></div></div>
    <div><h1>Deine <em>Aufgaben</em> für FC 27</h1>
      <p>Hake ab, was du erledigt hast. Oben siehst du immer zuerst, was bald abläuft – so verpasst du keine Belohnung.</p>
      <div class="kpis">
        <div class="kpi"><b>${open}</b><span>Aufgaben offen</span></div>
        <div class="kpi ${soon ? 'hot' : ''}"><b>${soon}</b><span>Enden in 3 Tagen</span></div>
        <div class="kpi"><b>${groupsDone} / ${live.length}</b><span>Gruppen fertig</span></div>
      </div></div>`;
  $('#topStats').innerHTML = `<b>${doneAll}</b><span class="lbl">/ ${tasksAll.length} Aufgaben</span>`;

  // Liste
  const list = live.filter(matches).sort(sorters[state.sort]);
  const el = $('#list');
  if (!list.length) {
    el.innerHTML = `<div class="empty"><b>Nichts gefunden</b>Probier einen anderen Filter oder Suchbegriff.</div>`;
    return;
  }
  const sec = (title, arr, cls = '') => arr.length ? `<div class="sec-h ${cls}"><h2>${title}</h2><span>${arr.length} Gruppen</span></div><div class="grid">${arr.map(card).join('')}</div>` : '';
  if (state.sort === 'expiry') {
    const soonL = list.filter(g => !isPerm(g) && endMs(g) - now() < 72 * 36e5);
    const timed = list.filter(g => !isPerm(g) && endMs(g) - now() >= 72 * 36e5);
    const perm = list.filter(isPerm);
    el.innerHTML = sec('Läuft bald ab', soonL, 'urgent') + sec('Zeitlich begrenzt', timed) + sec('Dauerhafte Ziele', perm);
  } else {
    el.innerHTML = `<div class="sec-h"><h2>Alle Aufgaben</h2><span>${list.length} Gruppen</span></div><div class="grid">${list.map(card).join('')}</div>`;
  }
}

function tick() {
  document.querySelectorAll('[data-timer]').forEach(e => {
    const g = DATA.find(x => x.id === e.dataset.timer); if (!g) return;
    const L = left(g); e.textContent = L.txt;
    const t = e.closest('.timer'); if (t) t.className = 'timer ' + L.cls;
  });
  const d = $('#dTimer');
  if (d && openId) { const g = DATA.find(x => x.id === openId); const L = left(g); d.textContent = L.txt; d.className = L.cls; }
}

/* ---------- Detail ---------- */
let openId = null;
function taskHTML(g, t) {
  const d = isDone(g, t);
  const pl = t.rewards.filter(r => r.kind === 'player');
  const ot = t.rewards.filter(r => r.kind !== 'player');
  const rw = (pl.length || ot.length) ? `<div class="t-rw"><span class="t-lbl">Belohnung</span>${pl.map(r => playerCard(r, 'sm')).join('')}${ot.map(r => chip(r)).join('')}</div>` : '';
  return `<li class="task ${d ? 'done' : ''}" data-t="${t.n}">
    <span class="cb"><input type="checkbox" ${d ? 'checked' : ''} aria-label="Aufgabe ${t.n} erledigt: ${esc(t.title)}"><span class="cb-box"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span></span>
    <div><div class="t-n">Aufgabe ${t.n}</div><div class="t-title">${esc(t.title)}</div><p class="t-desc">${esc(t.desc)}</p>${rw}</div></li>`;
}

function drawer(g) {
  const dc = doneCount(g), n = g.tasks.length, L = left(g);
  const perm = isPerm(g);
  const players = g.rewards.filter(r => r.kind === 'player');
  const others = g.rewards.filter(r => r.kind !== 'player');
  const startsTxt = Date.parse(g.starts) > now() ? `Startet ${fmtShort(g.starts)}` : `Gestartet ${fmtShort(g.starts)}`;
  const ends = perm ? `Unbefristet` : fmtDate(g.ends);
  return `
  <div class="d-head"><button class="d-back" data-close type="button">${SVG.back} Zurück</button>
    <div class="d-prog"><b id="dDone">${dc}</b> / ${n} Aufgaben</div></div>
  <div class="d-body">
    <span class="tag d-tag">${esc(g.cat)}</span>
    <h2 class="d-title" id="dTitle">${esc(g.title)}</h2>
    <p class="d-desc">${esc(g.desc)}</p>
    <div class="d-info">
      <div class="info"><small>Läuft ab</small><b class="${L.cls}" id="dTimerWrap"><span id="dTimer" class="${L.cls}">${L.txt}</span></b><span>${perm ? 'Dauerhaft verfügbar (bis ' + new Date(g.ends).getUTCFullYear() + ')' : esc(ends) + ' Uhr'}</span></div>
      <div class="info"><small>Zeitraum</small><b>${esc(fmtShort(g.starts))}</b><span>${perm ? 'läuft sehr lange' : 'bis ' + esc(fmtShort(g.ends))}</span></div>
      <div class="info"><small>Aufgaben</small><b>${n}</b><span>${startsTxt.replace(/^(Gestartet|Startet)/, 'Start:')}</span></div>
    </div>
    <h3 class="d-h">Gruppen-Belohnungen</h3>
    <div class="g-rewards">
      ${players.map(r => `<div class="pcw">${playerCard(r)}</div>`).join('')}
      ${others.map(r => chip(r, true)).join('')}
    </div>
    <h3 class="d-h">Checkliste <button type="button" id="markAll">Alle abhaken</button><button type="button" id="clearAll">Zurücksetzen</button></h3>
    <ul class="tasks" id="tasks">${g.tasks.map(t => taskHTML(g, t)).join('')}</ul>
    <div id="winBox">${dc === n ? '<div class="win">🏆 Geschafft – alles erledigt!</div>' : ''}</div>
  </div>`;
}

function openGroup(id, push = true) {
  const g = DATA.find(x => x.id === id); if (!g) return;
  openId = id;
  const dr = $('#drawer');
  dr.innerHTML = drawer(g);
  const accs = { Kampagnen: '#ff3d7f', Saison: '#d4ff3a', 'FC Pro': '#ffd23d', Grundlagen: '#3dffb0', Meilensteine: '#2ee6ff', Meisterschaft: '#b78cff', 'Live Events': '#ff8a3d' };
  dr.style.setProperty('--acc', accs[g.cat] || '#2ee6ff');
  $('#overlay').hidden = false;
  document.body.style.overflow = 'hidden';
  dr.scrollTop = 0;
  if (push && location.hash !== '#g' + id) history.pushState({ g: id }, '', '#g' + id);
  dr.focus && dr.setAttribute('tabindex', '-1');
}
function closeGroup(fromPop = false) {
  if (!openId) return;
  openId = null;
  $('#overlay').hidden = true;
  document.body.style.overflow = '';
  if (!fromPop && location.hash.startsWith('#g')) history.back();
  render();
}
function refreshDrawer(g) {
  const dc = doneCount(g), n = g.tasks.length;
  $('#dDone').textContent = dc;
  $('#winBox').innerHTML = dc === n ? '<div class="win">🏆 Geschafft – alles erledigt!</div>' : '';
  g.tasks.forEach(t => {
    const li = $(`#tasks [data-t="${t.n}"]`); if (!li) return;
    li.classList.toggle('done', isDone(g, t));
    li.querySelector('input').checked = isDone(g, t);
  });
}
function setTask(g, t, v) { if (v) state.done[key(g, t)] = true; else delete state.done[key(g, t)]; }

/* ---------- Events ---------- */
document.addEventListener('click', e => {
  const c = e.target.closest('.card[data-id]');
  if (c) return openGroup(c.dataset.id);
  if (e.target.closest('[data-close]')) return closeGroup();
  const ch = e.target.closest('.chip');
  if (ch) { state.cat = ch.dataset.cat; save(); return render(); }
  if (e.target.closest('.brand')) { e.preventDefault(); if (openId) closeGroup(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
  const g = openId && DATA.find(x => x.id === openId);
  if (g) {
    if (e.target.id === 'markAll') { g.tasks.forEach(t => setTask(g, t, true)); save(); refreshDrawer(g); }
    if (e.target.id === 'clearAll') { g.tasks.forEach(t => setTask(g, t, false)); save(); refreshDrawer(g); }
    const li = e.target.closest('.task');
    if (li && !e.target.closest('input')) {
      const t = g.tasks.find(x => String(x.n) === li.dataset.t);
      setTask(g, t, !isDone(g, t)); save(); refreshDrawer(g);
    }
  }
  if (e.target.id === 'resetAll') {
    if (confirm('Wirklich den gesamten Fortschritt zurücksetzen?')) { state.done = {}; save(); render(); }
  }
});
document.addEventListener('change', e => {
  const inp = e.target.closest('.task input'); if (!inp) return;
  const g = DATA.find(x => x.id === openId); const li = inp.closest('.task');
  const t = g.tasks.find(x => String(x.n) === li.dataset.t);
  setTask(g, t, inp.checked); save(); refreshDrawer(g);
});
$('#q').addEventListener('input', e => { state.q = e.target.value; render(); });
$('#sort').addEventListener('change', e => { state.sort = e.target.value; save(); render(); });
$('#hideDone').addEventListener('change', e => { state.hideDone = e.target.checked; save(); render(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && openId) closeGroup(); });
window.addEventListener('popstate', () => {
  const m = location.hash.match(/^#g(\d+)$/);
  if (m) openGroup(m[1], false); else if (openId) closeGroup(true);
});

/* ---------- Start ---------- */
$('#sort').value = state.sort; $('#hideDone').checked = state.hideDone; $('#q').value = '';
render();
const m0 = location.hash.match(/^#g(\d+)$/); if (m0) openGroup(m0[1], false);
setInterval(tick, 30000);
setInterval(() => { if (!openId) render(); }, 5 * 60000);
})();
