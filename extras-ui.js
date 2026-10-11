/* 補助資訊／標案資訊／產業報導：導覽分頁＋首頁區塊。資料：extras.js（XSUB、XTEN）與 data.js（NEWS 中 topic=產業報導）。 */
(function(){
var XH=decodeURIComponent((location.hash||'').slice(1));
var TABS=['補助資訊','標案資訊','產業報導'];
var SK='https://www.subsidyking.tw/',TK='https://web4.subsidyking.tw/';
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function wan(n){if(!n)return'';return n>=10000?(Math.round(n/1000)/10).toLocaleString()+' 萬元':n.toLocaleString()+' 元'}
function A(u,t,c){return u?'<a href="'+esc(u)+'" target="_blank" rel="noopener"'+(c?' class="'+c+'"':'')+'>'+t+'</a>':t}
function stTag(s){var c={'開放中':'go','即將開放':'go','招標中':'go','常態性/依公告':'nm','已截標':'nm','已決標':'nm','無法決標':'off','已截止':'off'}[s]||'nm';return '<span class="xtag x-'+c+'">'+esc(s)+'</span>'}
function sub(s){return '<article class="xcard"><div class="xmeta">'+stTag(s.status)+'<span>'+esc(s.org)+'</span></div><h3>'+A(s.url,esc(s.name))+'</h3>'+
 '<p class="xkv"><b>截止日</b>'+esc(s.deadline)+(s.amount?'　<b>金額</b>'+esc(s.amount):'　<b>金額</b>見原始公告')+'</p>'+
 (s.summary?'<p class="xsum">'+esc(s.summary)+'</p>':'')+(s.status=='已截止'&&s.est?'<p class="xkv"><b>預估下次開放</b>'+esc(s.est)+'</p>':'')+
 '<p class="xlinks">'+A(s.url,'原始連結 ↗','xsrc')+A(SK,'在補助王查看 ›','xk')+'</p></article>'}
function ten(t){return '<article class="xcard"><div class="xmeta">'+stTag(t.status)+'<span>'+esc(t.unit)+'</span><time>公告 '+esc(t.date)+'</time></div><h3>'+A(t.url,esc(t.title))+'</h3>'+
 '<p class="xkv"><b>預算</b>'+(t.budget?wan(t.budget):'未載明')+'　<b>截標日</b>'+(t.deadline||'未載明')+(t.award?'　<b>決標金額</b>'+wan(t.award):'')+'</p>'+
 (t.winner?'<p class="xkv"><b>得標廠商</b>'+esc(t.winner)+'</p>':'')+
 '<p class="xlinks">'+A(t.url,'原始公告 ↗','xsrc')+A(TK,'在標案王查看 ›','xk')+'</p></article>'}
function ind(n){return '<article class="xcard"><div class="xmeta"><span class="xtag x-ind">產業報導</span><span>'+esc(n.unit)+'</span><time>'+esc(n.date)+'</time></div><h3>'+A(n.url,esc(n.title))+'</h3><p class="xsum">'+esc(n.summary)+'</p><p class="xlinks">'+A(n.url,'原始連結 ↗','xsrc')+'</p></article>'}
var S=window.XSUB||[],T=window.XTEN||[],U=window.XUPD||{};
function I(){return (window.NEWS||[]).filter(function(n){return n.topic=='產業報導'&&!n.sample}).sort(function(a,b){return (b.date||'').localeCompare(a.date||'')})}
function note(x){if(x=='補助資訊')return '資料來源：<a href="'+SK+'" target="_blank" rel="noopener">補助王</a>補助資料庫，篩選本族群為主要對象或主辦機關的補助，每日更新（'+esc(U.date)+'）。內容以主辦機關公告為準。';
 if(x=='標案資訊')return '資料來源：<a href="'+TK+'" target="_blank" rel="noopener">標案王</a>（政府電子採購網公告，資料至 '+esc((U.tk||'').replace(/(\d{4})(\d\d)(\d\d)/,'$1-$2-$3'))+'），篩選本族群相關機關或案名，列招標中與近 60 天案件。以採購網公告為準。';
 return '本族群的產業發展與個人創業、事業發展新聞，摘要由編輯依原文整理，完整內容請看原始連結。'}
function view(x){var h='';
 if(x=='補助資訊'){var a=S.filter(function(s){return s.status!='已截止'}),b=S.filter(function(s){return s.status=='已截止'});
  h='<p class="xnote">'+note(x)+'</p><p class="xcount">現行 '+a.length+' 筆'+(b.length?'，已截止 '+b.length+' 筆（列在下方）':'')+'</p><div class="xlist">'+a.map(sub).join('')+'</div>'+(b.length?'<h3 class="xsubh">已截止（請留意下一期）</h3><div class="xlist xold">'+b.map(sub).join('')+'</div>':'')}
 else if(x=='標案資訊'){var o=T.filter(function(t){return t.status=='招標中'}),r=T.filter(function(t){return t.status!='招標中'});
  h='<p class="xnote">'+note(x)+'</p><p class="xcount">招標中 '+o.length+' 件，近期已截標／決標 '+r.length+' 件</p><h3 class="xsubh">招標中</h3><div class="xlist">'+(o.map(ten).join('')||'<p>目前沒有招標中的相關案件。</p>')+'</div><h3 class="xsubh">近期案件</h3><div class="xlist">'+r.map(ten).join('')+'</div>'}
 else {var n=I();h='<p class="xnote">'+note(x)+'</p><p class="xcount">共 '+n.length+' 則</p><div class="xlist">'+(n.map(ind).join('')||'<p>目前尚無已完成摘要的產業報導。</p>')+'</div>'}
 return '<h2 class="xtitle">'+x+'</h2>'+h}
var nav,xv,home;
function mark(x){[].forEach.call(nav.children,function(e){var on=e.getAttribute('data-x')==x;e.classList.toggle('on',on);if(on)e.setAttribute('aria-current','page');else if(x)e.removeAttribute('aria-current')})}
function show(x){xv.innerHTML=view(x);xv.hidden=false;['#home','#catview'].forEach(function(s){var e=document.querySelector(s);if(e)e.hidden=true});mark(x);
 if(decodeURIComponent(location.hash.slice(1))!=x)history.pushState(null,'','#'+x);scrollTo(0,0)}
function hide(){if(xv&&!xv.hidden){xv.hidden=true;mark('')}}
function blocks(){var m=document.querySelector('#home .maincol');if(!m)return;
 if(m.id){var w=document.createElement('div');w.className='xhome';m.parentNode.parentNode.appendChild(w);m=w}
 var cfg=[['補助資訊',S.filter(function(s){return s.status!='已截止'}).slice(0,4),sub],['標案資訊',T.slice(0,4),ten],['產業報導',I().slice(0,4),ind]];
 cfg.forEach(function(c){if(!c[1].length)return;var s=document.createElement('section');s.className='xblock';
  s.innerHTML='<h2><span>'+c[0]+'</span><a href="#'+c[0]+'" data-x="'+c[0]+'">更多 ›</a></h2><div class="xgrid">'+c[1].map(c[2]).join('')+'</div>';m.appendChild(s)})}
document.addEventListener('DOMContentLoaded',function(){
 nav=document.querySelector('#tabs')||document.querySelector('.catnav .wrap');home=document.querySelector('#home');if(!nav||!home)return;
 var tag=(nav.querySelector('button')?'button':'a');
 TABS.forEach(function(x){var e=document.createElement(tag);e.setAttribute('data-x',x);e.textContent=x;if(tag=='a')e.href='#'+x;else e.type='button';nav.appendChild(e)});
 xv=document.createElement('section');xv.id='xview';xv.hidden=true;var cv=document.querySelector('#catview');cv.parentNode.insertBefore(xv,cv.nextSibling);
 blocks();
 document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('[data-x]');
  if(t){e.preventDefault();e.stopImmediatePropagation();show(t.getAttribute('data-x'));return}
  var o=e.target.closest&&e.target.closest('[data-c],[data-go],.catnav a,.catnav button');if(o)hide()},true);
 addEventListener('popstate',function(){var h=decodeURIComponent(location.hash.slice(1));if(TABS.indexOf(h)>=0)show(h);else hide()});
 addEventListener('hashchange',function(){var h=decodeURIComponent(location.hash.slice(1));if(TABS.indexOf(h)<0)hide()});
 if(TABS.indexOf(XH)>=0)setTimeout(function(){show(XH)},0);
});
var st=document.createElement('style');st.textContent=
'#xview{padding:8px 0 24px}.xtitle{font:900 24px/1.4 var(--serif,serif);border-bottom:2px solid currentColor;padding-bottom:6px;margin:8px 0 12px}'+
'.xblock{margin:0 0 32px}.xblock h2{display:flex;justify-content:space-between;align-items:baseline;font:900 22px/1.4 var(--serif,serif);border-bottom:2px solid currentColor;padding-bottom:6px;margin:0 0 16px}'+
'.xblock h2 span{border-left:6px solid #b8860b;padding-left:10px}.xblock h2 a{font:500 14px var(--sans,sans-serif);opacity:.75}'+
'.xgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}.xlist{display:grid;gap:14px}'+
'.xcard{background:#fff;border:1px solid #e3e0da;padding:14px 16px;display:flex;flex-direction:column;color:#1a1a1a}.xcard h3{font:700 17px/1.5 var(--serif,serif);margin:6px 0}'+
'.xmeta{font-size:13px;color:#666;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.xkv{margin:0 0 6px;font-size:14px}.xkv b{color:#555;margin-right:4px;font-weight:600}'+
'.xsum{margin:0 0 8px;font-size:15px;color:#333}.xlinks{margin:auto 0 0;display:flex;gap:14px;flex-wrap:wrap;font-size:14px;font-weight:600}.xsrc{color:#b3122e}.xk{color:#1f4e8c}'+
'.xtag{color:#fff;padding:1px 8px;border-radius:2px;font-weight:600;font-size:12px}.x-go{background:#2e7d4f}.x-nm{background:#6b6b6b}.x-off{background:#a33}.x-ind{background:#b8860b}'+
'.xnote{font-size:14px;color:#555;margin:0 0 6px}.xcount{font-weight:600;margin:0 0 12px}.xsubh{font:700 18px var(--serif,serif);margin:22px 0 10px}.xold .xcard{opacity:.8}';
document.head.appendChild(st);
})();
