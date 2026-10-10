const ORDER = window.HGNN.ORDER, DEK = window.HGNN.DEK;
const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const root = document.getElementById('article');

function one(n) {
  document.title = n.title + '｜客家全球新聞網';
  const back = './#' + encodeURIComponent(n.category);
  root.innerHTML = `<article class="article-body">
    <div class="meta"><span class="badge-sample">虛構情境</span><span class="tag" data-cat="${esc(n.category)}">${esc(n.category)}</span><span class="unit">${esc(n.unit)}</span><time datetime="${esc(n.date)}">${esc(n.date)}</time></div>
    <h1>${esc(n.title)}</h1>
    <p class="lede">${esc(n.summary)}</p>
    <div class="callout">
      <p>這一則沒有原文、沒有受訪者、沒有統計，也不能外連到任何新聞網站。它只示範「${esc(n.category)}」欄目的標題和摘要會佔多少版面。</p>
      <p>${esc(DEK[n.category] || '')}正式刊出時，每一則都會附上原發布單位的連結，著作權屬於原單位。摘要只改寫公開資訊，不添加原文沒有的人名或數字。</p>
    </div>
    <p><a href="${back}">回到${esc(n.category)}</a>　<a href="article.html">全部範例稿</a></p>
  </article>`;
}
function index() {
  document.title = '範例稿一覽｜客家全球新聞網';
  const items = window.NEWS || [];
  root.innerHTML = `<header class="page"><h1>範例稿一覽</h1><p class="lede">以下全部是虛構情境，用來審查欄目與摘要長度。不是新聞。</p></header>` +
    ORDER.map(c => {
      const list = items.filter(n => n.category === c);
      if (!list.length) return '';
      return `<section><h2>${esc(c)}</h2><p class="dek">${esc(DEK[c] || '')}</p><ul class="catalog">` +
        list.map(n => `<li><a href="article.html#${encodeURIComponent(n.id)}">${esc(n.title)}</a><div class="meta"><time datetime="${esc(n.date)}">${esc(n.date)}</time><span>${esc(n.unit)}</span></div></li>`).join('') +
        '</ul></section>';
    }).join('');
}
function render() {
  const id = decodeURIComponent((location.hash || '').replace(/^#/, ''));
  const n = (window.NEWS || []).find(x => x.id === id);
  if (n) one(n); else index();
}
addEventListener('hashchange', render);
render();
