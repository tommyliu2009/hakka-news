(function () {
  var FONT_KEY = 'hgnn-font';
  var CONTRAST_KEY = 'hgnn-contrast';
  var sizes = ['100%', '112.5%', '125%'];
  var font = 0;
  try { font = parseInt(localStorage.getItem(FONT_KEY) || '0', 10); } catch (e) {}
  if (!(font >= 0 && font < sizes.length)) font = 0;

  function applyFont() {
    document.documentElement.style.fontSize = sizes[font];
    try { localStorage.setItem(FONT_KEY, String(font)); } catch (e) {}
    var dec = document.getElementById('font-dec');
    var inc = document.getElementById('font-inc');
    if (dec) dec.setAttribute('aria-disabled', font === 0 ? 'true' : 'false');
    if (inc) inc.setAttribute('aria-disabled', font === sizes.length - 1 ? 'true' : 'false');
  }
  function applyContrast() {
    var on = document.documentElement.getAttribute('data-contrast') === 'more';
    var btn = document.getElementById('contrast');
    if (!btn) return;
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.textContent = on ? '一般對比' : '提高對比';
  }
  applyFont();
  applyContrast();
  var el = document.getElementById('today');
  if (el) {
    var d = new Date();
    var w = '日一二三四五六';
    el.textContent = d.getFullYear() + '年' + (d.getMonth() + 1) + '月' + d.getDate() + '日 星期' + w[d.getDay()];
  }
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.id) return;
    if (t.id === 'font-inc') { font = Math.min(sizes.length - 1, font + 1); applyFont(); }
    if (t.id === 'font-dec') { font = Math.max(0, font - 1); applyFont(); }
    if (t.id === 'contrast') {
      var on = document.documentElement.getAttribute('data-contrast') === 'more';
      if (on) document.documentElement.removeAttribute('data-contrast');
      else document.documentElement.setAttribute('data-contrast', 'more');
      try { localStorage.setItem(CONTRAST_KEY, on ? '' : 'more'); } catch (err) {}
      applyContrast();
    }
  });
})();
