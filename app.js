const ORDER = window.HGNN.ORDER, DEK = window.HGNN.DEK;
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const N = [...(window.NEWS || [])].sort((a, b) => (b.date || '').localeCompare(a.date || '') || (b.id || '').localeCompare(a.id || ''));
let cat = '首頁', unit = '', shown = 3, booted = false;

const upd = $('#upd');
if (upd) upd.textContent = '資料更新：' + (window.UPDATED || '尚無') + (N.length && N.every(n => n.sample) ? '（展示樣本）' : '');

const hrefOf = n => n.sample ? 'article.html#' + encodeURIComponent(n.id) : n.url;
const srcText = n => n.sample ? '閱讀範例說明' : '原始連結';
const srcAttrs = n => n.sample ? '' : ' target="_blank" rel="noopener noreferrer"';
const meta = n => {
  const badge = n.sample ? '<span class="badge-sample">虛構情境</span>' : '';
  return `<div class="meta">${badge}<span class="tag" data-cat="${esc(n.category)}">${esc(n.category)}</span><span class="unit">${esc(n.unit)}</span><time datetime="${esc(n.date)}">${esc(n.date)}</time></div>`;
};
const card = (n, cls = 'card') => `<article class="${cls}">${meta(n)}<h3><a href="${esc(hrefOf(n))}"${srcAttrs(n)}>${esc(n.title)}</a></h3><p class="sum">${esc(n.summary)}</p><button type="button" class="tog" aria-expanded="false">展開摘要</button><a class="src" href="${esc(hrefOf(n))}"${srcAttrs(n)}>${srcText(n)}</a></article>`;

function side() {
  const units = {};
  N.forEach(n => {
    units[n.category] = units[n.category] || {};
    units[n.category][n.unit] = (units[n.category][n.unit] || 0) + 1;
  });
  let h = '<div class="box"><h3>關於這個展示版</h3><p>卡片都是虛構範例。正式欄目會改放可查證的公開資訊，並附上原始連結。</p><p><a href="about.html">閱讀宗旨與編輯原則</a></p></div>';
  h += '<div class="box"><h3>來源單位</h3>';
  h += ORDER.filter(c => units[c]).map(c => {
    const list = Object.entries(units[c]).sort((a, b) => b[1] - a[1]).map(([u, k]) =>
      `<li><a href="./#${encodeURIComponent(c)}" data-c="${esc(c)}" data-u="${esc(u)}" class="${c === cat && u === unit ? 'on' : ''}">${esc(u)}<em>${k}</em></a></li>`
    ).join('');
    return `<p class="grp">${esc(c)}</p><ul class="units">${list}</ul>`;
  }).join('') + '</div>';
  h += '<div class="box"><h3>最新範例</h3><ol class="latest">' + N.slice(0, 8).map(n =>
    `<li><a href="${esc(hrefOf(n))}">${esc(n.title)}</a><time datetime="${esc(n.date)}">${esc(n.date)}｜${esc(n.unit)}</time></li>`
  ).join('') + '</ol></div>';
  $$('.side').forEach(s => { s.innerHTML = h; });
}
function home() {
  const [l, ...r] = N;
  const lead = $('#lead');
  if (!l) {
    lead.innerHTML = '<p class="empty">目前沒有可顯示的資料。</p>';
    $('#subs').innerHTML = '';
    $('#blocks').innerHTML = '';
    return;
  }
  lead.innerHTML = `<article class="lead">${meta(l)}<h2><a href="${esc(hrefOf(l))}">${esc(l.title)}</a></h2><p class="sum">${esc(l.summary)}</p><button type="button" class="tog" aria-expanded="false">展開摘要</button><a class="src" href="${esc(hrefOf(l))}">閱讀範例說明</a></article>`;
  $('#subs').innerHTML = '<h2 class="kicker">焦點</h2>' + r.slice(0, 4).map(n =>
    `<article class="subh">${meta(n)}<h3><a href="${esc(hrefOf(n))}">${esc(n.title)}</a></h3></article>`
  ).join('');
  $('#blocks').innerHTML = ORDER.map(c => {
    const a = N.filter(n => n.category === c).slice(0, 3);
    if (!a.length) return '';
    return `<section class="block" data-cat="${esc(c)}"><h2><span>${esc(c)}</span><a href="./#${encodeURIComponent(c)}" data-go="${esc(c)}">更多</a></h2><p class="dek">${esc(DEK[c] || '')}</p><div class="grid">${a.map(n => card(n)).join('')}</div></section>`;
  }).join('');
}
function catv() {
  const a = N.filter(n => n.category === cat && (!unit || n.unit === unit));
  $('#ctitle').textContent = cat + (unit ? '｜' + unit : '');
  $('#cdek').textContent = DEK[cat] || '';
  const clear = unit ? ` <a href="./#${encodeURIComponent(cat)}" data-c="${esc(cat)}" data-u="">顯示全部單位</a>` : '';
  $('#cmeta').innerHTML = `共 ${a.length} 則範例` + clear;
  $('#clist').innerHTML = a.length
    ? a.slice(0, shown).map(n => card(n, 'card row')).join('')
    : '<p class="empty">這個條件目前沒有稿件。</p>';
  const more = $('#more');
  more.hidden = a.length <= shown;
}
function folds() {
  $$('.sum').forEach(p => {
    const b = p.nextElementSibling;
    if (!b || !b.classList.contains('tog')) return;
    if (p.closest('[hidden]')) return;
    const overflow = p.scrollHeight > p.clientHeight + 2;
    b.hidden = !overflow && !p.classList.contains('open');
  });
}
function hashCat() {
  const h = decodeURIComponent((location.hash || '').replace(/^#/, ''));
  return ORDER.includes(h) ? h : '首頁';
}
function go(c, u, replace) {
  if (c !== '首頁' && !ORDER.includes(c)) c = '首頁';
  cat = c;
  unit = u || '';
  if (cat === '首頁') unit = '';
  shown = 3;
  $$('#tabs a').forEach(a => {
    const on = a.dataset.c === cat;
    a.classList.toggle('on', on);
    if (on) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  $('#home').hidden = cat !== '首頁';
  $('#catview').hidden = cat === '首頁';
  if (cat === '首頁') home(); else catv();
  side();
  folds();
  if (hashCat() !== cat) {
    const url = cat === '首頁' ? location.pathname : '#' + encodeURIComponent(cat);
    history[replace ? 'replaceState' : 'pushState']({c: cat}, '', url);
  }
  if (booted) {
    const focusTarget = cat === '首頁' ? $('#lead') : $('#ctitle');
    if (focusTarget) {
      focusTarget.setAttribute('tabindex', '-1');
      focusTarget.focus({preventScroll: true});
    }
    scrollTo(0, 0);
  }
  booted = true;
}
document.addEventListener('click', e => {
  const t = e.target.closest('[data-c],[data-go],.tog');
  if (!t) return;
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
  if (t.classList.contains('tog')) {
    const p = t.previousElementSibling;
    const o = p.classList.toggle('open');
    t.setAttribute('aria-expanded', o ? 'true' : 'false');
    t.textContent = o ? '收合摘要' : '展開摘要';
    return;
  }
  e.preventDefault();
  go(t.dataset.go || t.dataset.c, t.dataset.u || '', false);
});
$('#more').addEventListener('click', () => { shown += 6; catv(); folds(); });
addEventListener('resize', folds);
addEventListener('popstate', () => {
  const h = decodeURIComponent((location.hash || '').replace(/^#/, ''));
  go(ORDER.includes(h) ? h : '首頁', '', true);
});
go(hashCat(), '', true);
