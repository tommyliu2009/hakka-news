#!/usr/bin/env python3
"""客家全球新聞網：抓取官方與中央社公開來源，用客家相關關鍵字篩選。
抓到的項目只進 news_db.json，summary_ok 為 false，不會出現在網站上。
須由編輯核對原文、寫成 50～200 字摘要，再用 apply_summaries.py 寫回。
不得把未查證的人名、引述或數字補進摘要。
用法: python3 fetch_news.py [天數，預設30]"""
import sys, json, re, time, html, datetime as dt, urllib.parse, concurrent.futures as cf
import feedparser, requests, ssl
from requests.adapters import HTTPAdapter
class _SSLAdapter(HTTPAdapter):
    # 台灣政府憑證常缺 SKI 等欄位，Python 3.13 嚴格模式會拒絕；仍驗證憑證，只關閉 strict 旗標
    def init_poolmanager(self, *a, **k):
        ctx = ssl.create_default_context(); ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        k['ssl_context'] = ctx; return super().init_poolmanager(*a, **k)
_S = requests.Session(); _S.mount('https://', _SSLAdapter())
try:
    from googlenewsdecoder import gnewsdecoder
except ImportError:
    gnewsdecoder = None
from pubdate import extract as extract_pubdate
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
DB = 'news_db.json'; STATUS = 'source_status.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36'}
KW = ['客家','客語','客庄','客家族群','客家話','客委會','桐花','義民','天穿日','藍衫']
STRONG = ['客家','客語','客庄','客家族群','客家話','客委會','四縣腔','海陸腔','大埔腔','饒平腔','詔安腔','桐花','義民祭','天穿日']

def _shared_rss(u):
    """共用 RSS 快取（/workspace/shared-data/rss_cache，3 小時內同來源只抓一次）；共用區有問題就直接連網。"""
    try:
        sys.path.insert(0, '/workspace/shared-data'); import shared
        return shared.rss(u, _S, UA)
    except Exception:
        r = _S.get(u, headers=UA, timeout=25); return r.status_code, r.content

RSS = {  # 名稱: (網址, 類別)
 '內政部移民署': ('https://www.immigration.gov.tw/5385/7445/rss', '中央'),
 '行政院': ('https://www.ey.gov.tw/RSS_Content.aspx?ModuleType=7', '中央'),
 '衛生福利部': ('https://www.mohw.gov.tw/rss-16-1.html', '中央'),
 '教育部': ('https://www.edu.tw/Rss_News.aspx', '中央'),
 '中央社-政治': ('https://feeds.feedburner.com/rsscna/politics', '媒體'),
 '中央社-社會': ('https://feeds.feedburner.com/rsscna/social', '媒體'),
 '中央社-地方': ('https://feeds.feedburner.com/rsscna/local', '媒體'),
 '中央社-國際': ('https://feeds.feedburner.com/rsscna/intworld', '媒體'),
 '中央社-生活': ('https://feeds.feedburner.com/rsscna/lifehealth', '媒體'),
}
GQ_SITES = ['site:gov.tw', 'site:cna.com.tw', 'site:hakka.gov.tw', 'site:gov.taipei']
COUNTY_SITES = ['ntpc.gov.tw','tycg.gov.tw','taichung.gov.tw','tainan.gov.tw','kcg.gov.tw','klcg.gov.tw','hccg.gov.tw','hsinchu.gov.tw',
 'miaoli.gov.tw','chcg.gov.tw','nantou.gov.tw','yunlin.gov.tw','chiayi.gov.tw','cyhg.gov.tw','pthg.gov.tw','e-land.gov.tw','hl.gov.tw',
 'taitung.gov.tw','penghu.gov.tw','kinmen.gov.tw','matsu.gov.tw','mol.gov.tw','ocac.gov.tw','moi.gov.tw']
GQ_KW = ['客家','客語','客庄','客委會','桐花','義民祭','天穿日']
COUNTY = {'taipei':'臺北市','ntpc':'新北市','tycg':'桃園市','taichung':'臺中市','tainan':'臺南市','kcg':'高雄市','klcg':'基隆市',
 'hccg':'新竹市','hsinchu':'新竹縣','miaoli':'苗栗縣','chcg':'彰化縣','nantou':'南投縣','yunlin':'雲林縣','chiayi':'嘉義市',
 'cyhg':'嘉義縣','cyc':'嘉義縣','pthg':'屏東縣','e-land':'宜蘭縣','ilan':'宜蘭縣','hl':'花蓮縣','hualien':'花蓮縣','taitung':'臺東縣',
 'penghu':'澎湖縣','kinmen':'金門縣','matsu':'連江縣'}
CENTRAL = {'immigration':'內政部移民署','moi':'內政部','mol':'勞動部','wda':'勞動部勞動力發展署','edu':'教育部','mohw':'衛生福利部',
 'ocac':'僑務委員會','ey':'行政院','moj':'法務部','mofa':'外交部','boca':'外交部領事事務局','npa':'內政部警政署','nhi':'衛福部健保署',
 'president':'總統府','moea':'經濟部','mac':'大陸委員會','cip':'原住民族委員會','moc':'文化部','sa':'教育部體育署','k12ea':'教育部國教署'}

def norm_date(s):
    try:
        t = time.strptime(s[:25].strip(), '%a, %d %b %Y %H:%M:%S') if s else None
    except Exception:
        t = None
    return t

def classify(url, src_name=''):
    host = urllib.parse.urlparse(url).netloc.lower()
    if 'cna.com.tw' in host: return '媒體', '中央社'
    if host.endswith('gov.taipei'): return '地方', '臺北市'
    parts = host.split('.')
    if 'gov' in parts:
        i = parts.index('gov'); org = parts[i-1] if i > 0 else ''
        subs = parts[:i]
        for p in reversed(subs):
            if p in COUNTY: return '地方', COUNTY[p]
        for p in reversed(subs):
            if p in CENTRAL: return '中央', CENTRAL[p]
        return '中央', src_name or host
    return '媒體', src_name or host

# 分類依主題，不依中央／地方／媒體。順序越前面越優先。
TOPICS = [
    ('政策與補助', ['補助', '獎助', '要點', '預算', '津貼', '補貼', '申請', '政策']),
    ('客語推廣', ['客語', '客家語', '母語', '認證', '四縣', '海陸', '大埔', '饒平', '詔安', '教學']),
    ('節慶活動', ['桐花', '義民', '天穿', '豐年', '節慶', '祭典', '踩街']),
    ('產業與觀光', ['觀光', '旅遊', '產業', '商圈', '農產', '市集', '民宿']),
    ('全球客家', ['海外', '僑', '全球客家', '馬來西亞', '新加坡', '印尼']),
    ('客庄新聞', ['客庄', '鄉鎮', '村里']),
    ('客家文化', ['文化', '文資', '保存', '工藝', '美食', '音樂', '戲曲', '藍染', '山歌']),
]
def topic_of(text):
    for name, kws in TOPICS:
        if any(k in text for k in kws):
            return name
    return '客家文化'


# ---- 非新聞過濾規則 ----
BAD_URL = re.compile(r'(coa\.immigration|-frontend|niaicinfo|/apply|/verify|/login|Download\.ashx|getFile|/Attachment/|/media/|\.pdf|\.docx?|\.xlsx?|\.ods|\.odt|'
 r'data\.[a-z]+\.gov\.tw|pxweb|statdb|/DataSet/|/Resource/|faq|/viewService/|/app/map|socmap|nhicore|law-out|LawContent|/egFront/|gazette\.nat|'
 r'export|Video_Content|News_Video|/tag/|servicestation\.immigration\.gov\.tw/\d+/?$|/bidding/|/File/|judicial\.gov\.tw/tw/cp-144|/cp\.aspx|/business/)', re.I)
BAD_TITLE = re.compile(r'(^\s*-|中文網$|線上申辦|申辦系統|Online Application|Application System|Gold Card|- Immigration|專區$|專區\s*-|服務站-|事務大隊-|關鍵字新聞|常見問答|如何辦理|如何處理|須知|嗎[？?]|要幾分|呢[？?]|'
 r'統計|人數|一覽表|表格[:：]|報告$|會議紀錄|會議記錄|錄取|徵.*社工|約用|採購|勞務|問卷|公示送達|登記|系統維護|日程表|機構資訊|影音|微電影|影片|海報|表\s*\d+|'
 r'作業流程|檢送|名冊|影本|居留證號|免徵|富豪|業務專區|政治獻金法-)')
def is_news(title, url):
    return not BAD_URL.search(url or '') and not BAD_TITLE.search(title or '')

def relevant(text):
    return any(k in text for k in STRONG)

def get_meta_summary(url, title=''):
    """回傳 (摘要, 狀態, 原文發布日)"""
    try:
        r = _S.get(url, headers=UA, timeout=20); r.encoding = r.apparent_encoding if not r.encoding or r.encoding.lower()=='iso-8859-1' else r.encoding
        if r.status_code != 200: return None, f'HTTP {r.status_code}', None
        h = r.text; s = ''; pd = extract_pubdate(url, h, title)
        for pat in [r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)', r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
                    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:)?description']:
            m = re.search(pat, h, re.I)
            if m and len(m.group(1).strip()) > 20: s = m.group(1); break
        if not s:
            ps = [re.sub('<[^>]+>', '', p) for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S|re.I)]
            ps = [html.unescape(p).strip() for p in ps if len(p.strip()) > 40]
            s = ps[0] if ps else ''
        s = re.sub(r'\s+', ' ', html.unescape(s)).strip()
        return (s[:100] + ('…' if len(s) > 100 else '')) if s else '', 'ok', pd
    except Exception as e:
        return None, type(e).__name__, None

def main():
    try: db = json.load(open(DB))
    except Exception: db = {}
    status = {}; cand = []
    cutoff = time.time() - DAYS*86400
    for name, (u, cat) in RSS.items():
        try:
            sc, body = _shared_rss(u); f = feedparser.parse(body)
            if sc != 200 or not f.entries: raise Exception(f'HTTP {sc}, {len(f.entries)} 則')
            n = 0
            for e in f.entries:
                txt = (e.get('title','') + ' ' + re.sub('<[^>]+>','',e.get('summary','')))
                if relevant(txt):
                    cand.append(dict(title=e.title.strip(), url=e.link, pub=e.get('published_parsed'), src=name.split('-')[0], desc=re.sub('<[^>]+>','',e.get('summary','')))); n += 1
            status[name] = {'ok': True, 'note': f'{len(f.entries)} 則，相關 {n}'}
        except Exception as ex:
            status[name] = {'ok': False, 'note': str(ex)[:120]}
    for site in GQ_SITES:
        tot = 0
        for k in GQ_KW:
            q = urllib.parse.quote(f'{k} {site} when:{DAYS}d')
            try:
                f = feedparser.parse(_S.get(f'https://news.google.com/rss/search?q={q}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant', headers=UA, timeout=25).content)
                for e in f.entries:
                    t = re.sub(r'\s+-\s+[^-]+$', '', e.title).strip()
                    if not relevant(t + k if k in ('居留證','歸化') else t): continue
                    cand.append(dict(title=t, url=None, glink=e.link, pub=e.get('published_parsed'), src=e.get('source',{}).get('title',''), desc=''))
                    tot += 1
            except Exception as ex:
                status[f'Google News {site} {k}'] = {'ok': False, 'note': str(ex)[:100]}
            time.sleep(1)
        status[f'官方/中央社索引 ({site})'] = {'ok': tot > 0, 'note': f'候選 {tot} 則'}
    for site in COUNTY_SITES:
        q = urllib.parse.quote(f'(客家 OR 客語 OR 客庄 OR 客委會) site:{site} when:{DAYS}d'); n = 0
        try:
            f = feedparser.parse(_S.get(f'https://news.google.com/rss/search?q={q}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant', headers=UA, timeout=25).content)
            for e in f.entries:
                t = re.sub(r'\s+-\s+[^-]+$', '', e.title).strip()
                if relevant(t): cand.append(dict(title=t, url=None, glink=e.link, pub=e.get('published_parsed'), src=e.get('source',{}).get('title',''), desc='')); n += 1
            status[f'索引 {site}'] = {'ok': True, 'note': f'相關 {n}'}
        except Exception as ex:
            status[f'索引 {site}'] = {'ok': False, 'note': str(ex)[:100]}
        time.sleep(1)
    # 去重（標題）
    try: rejected = set(json.load(open('rejected.json')))
    except Exception: rejected = set()
    known_titles = {v['title'] for v in db.values()} | rejected
    seen = set(); todo = []
    for c in cand:
        if not c['pub'] or time.mktime(c['pub']) < cutoff: continue
        key = re.sub(r'\W', '', c['title'])[:40]
        if key in seen or c['title'] in known_titles: continue
        seen.add(key); todo.append(c)
    print('新候選', len(todo))
    if gnewsdecoder is None and any(c['url'] is None for c in todo):
        print('未安裝 googlenewsdecoder，略過 Google 新聞連結')
    for c in todo:
        if c['url'] is None and gnewsdecoder is not None:
            try:
                d = gnewsdecoder(c['glink'], interval=1); c['url'] = d.get('decoded_url') if d.get('success') else None
            except Exception: c['url'] = None
    try: rej_urls = set(json.load(open('rejected_urls.json')))
    except Exception: rej_urls = set()
    keep = []
    for c in todo:
        if not c['url'] or c['url'] in rej_urls: continue
        if not c.get('pub') or not is_news(c['title'], c['url']): rejected.add(c['title']); continue
        keep.append(c)
    todo = keep
    fail_hosts = {}
    def work(c):
        s, st, pd = get_meta_summary(c['url'], c['title']); return c, s, st, pd
    cutoff_date = (dt.date.today() - dt.timedelta(days=DAYS)).isoformat()
    no_date = 0
    with cf.ThreadPoolExecutor(8) as ex:
        for c, s, st, pd in ex.map(work, todo):
            host = urllib.parse.urlparse(c['url']).netloc
            # 一律以原文頁面上的發布日為準；取不到（含原文打不開）就不收，下次再試
            if not pd:
                no_date += 1
                if s is None: fail_hosts.setdefault(host, [0, st])[0] += 1
                continue
            if pd < cutoff_date: rejected.add(c['title']); continue
            if s is None:
                fail_hosts.setdefault(host, [0, st])[0] += 1
                d = re.sub(r'\s+', ' ', html.unescape(c.get('desc') or '')).strip()
                s = (d[:100] + ('…' if len(d) > 100 else '')) if len(d) > 20 else ''
                if not s and c['src'] not in RSS and not any(x in c['url'] for x in ('News_Content','cna.com.tw','/post','News/Detail','NewsDetail','newsdetail','bulletin')): rejected.add(c['title']); continue
            _level, unit = classify(c['url'], c['src'])
            text = c['title'] + ' ' + (s or '')
            if not relevant(text): rejected.add(c['title']); continue
            cat = topic_of(text)
            date = pd
            # 暫時摘要不上線。編輯須核對原文屬實，寫成 50～200 字，再用 apply_summaries.py 寫回。
            db[c['url']] = dict(title=c['title'], url=c['url'], date=date, category=cat, unit=unit, summary=s, summary_ok=False, sample=False,
                                added=dt.datetime.now().strftime('%Y-%m-%d'))
    json.dump(sorted(rejected), open('rejected.json','w'), ensure_ascii=False)
    json.dump(db, open(DB, 'w'), ensure_ascii=False, indent=0)
    status['_原文取不到發布日（未收錄）'] = {'ok': True, 'note': f'{no_date} 則'}
    status['_原文無法讀取的網站（未收錄）'] = {'ok': not fail_hosts, 'note': '; '.join(f'{h} {n}則({e})' for h,(n,e) in fail_hosts.items())}
    json.dump(dict(updated=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), sources=status), open(STATUS,'w'), ensure_ascii=False, indent=1)
    pend = [dict(url=u, title=v['title'], date=v['date'], unit=v['unit'], hint=v.get('summary','')) for u, v in db.items() if not v.get('summary_ok')]
    json.dump(pend, open('pending_summary.json','w'), ensure_ascii=False, indent=1)
    print('資料庫共', len(db), '則；待寫摘要（未上線）', len(pend), '則 → pending_summary.json')
if __name__ == '__main__':
    main()
