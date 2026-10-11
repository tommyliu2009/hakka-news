#!/usr/bin/env python3
"""產業報導：抓本族群的產業發展／個人創業新聞（中央社、政府網站、權威媒體），並把資料庫中符合的新聞標記 topic=產業報導。
用法: python3 fetch_industry.py [天數，預設3]   抓新稿＋重新標記
      python3 fetch_industry.py --retag        只重新標記（不連網）
新稿一律 summary_ok=False，須依原文寫 50～200 字摘要並用 apply_summaries.py 套用後才會上線。"""
import sys, os, json, re, time, urllib.parse, datetime as dt, concurrent.futures as cf
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.basename(os.getcwd())
CFG = {
 'immigrant-news': dict(group=['新住民','新移民','外籍配偶','外配','陸配','移工','新二代','東南亞','越南籍','印尼籍','泰籍','菲律賓籍','緬甸'],
     q=['新住民 創業','新住民 開店','新住民 產業','新住民 小吃','新二代 創業','移工 創業','新住民 品牌','東南亞 新住民 餐廳'],
     media=['site:cna.com.tw','site:gov.tw','site:pts.org.tw','site:news.pts.org.tw']),
 'hakka-news': dict(group=['客家','客庄','客語','浪漫台三線','六堆','客委會'],
     q=['客家 產業','客庄 創業','客家 青年 返鄉','客庄 產業','客家 品牌','客家 美食 產業','浪漫台三線 產業','客庄 創生'],
     media=['site:cna.com.tw','site:gov.tw','site:pts.org.tw','site:hakkatv.org.tw']),
 'indigenous-news': dict(group=['原住民','原民','部落','族人','原鄉','阿美','泰雅','排灣','布農','太魯閣','達悟','賽德克','卑南','魯凱','鄒族','賽夏'],
     q=['原住民 產業','部落 經濟','原住民 創業','部落 產業','原住民 品牌','原鄉 產業','部落 觀光','原住民族 經濟'],
     media=['site:cna.com.tw','site:gov.tw','site:pts.org.tw','site:titv.ipcf.org.tw']),
}[SITE]
IND = ['創業','開店','產業','商機','品牌','農特產','農產品','經濟','市集','事業','老闆','青創','創生','產值','電商','行銷','展售','餐廳','小吃',
       '咖啡','伴手禮','文創','觀光工廠','營收','商圈','職人','店家','加工','銷售','商品','民宿','返鄉創','金融','數位轉型','證照']
NOT = ['職安','人權','遣返','詐騙','犯罪','逃逸','查獲']
def is_industry(text):
    return any(k in text for k in CFG['group']) and any(k in text for k in IND) and not any(k in text for k in NOT)

def retag(db):
    n = 0
    for v in db.values():
        if v.get('sample'): continue
        t = v.get('title', '')
        if is_industry(t): v['topic'] = '產業報導'; n += 1
        elif v.get('topic') == '產業報導' and not v.get('topic_fixed'): v.pop('topic')
    return n

def fetch(days):
    import feedparser, fetch_news as F
    from googlenewsdecoder import gnewsdecoder
    db = json.load(open('news_db.json'))
    try: rejected = set(json.load(open('rejected.json')))
    except Exception: rejected = set()
    try: rej_urls = set(json.load(open('rejected_urls.json')))
    except Exception: rej_urls = set()
    known = {v['title'] for v in db.values()} | rejected
    cand, seen = [], set()
    cutoff = time.time() - days * 86400
    for site in CFG['media']:
        for q in CFG['q']:
            qq = urllib.parse.quote(f'{q} {site} when:{days}d')
            try:
                f = feedparser.parse(F._S.get(f'https://news.google.com/rss/search?q={qq}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant', headers=F.UA, timeout=25).content)
            except Exception: continue
            for e in f.entries:
                t = re.sub(r'\s+-\s+[^-]+$', '', e.title).strip()
                k = re.sub(r'\W', '', t)[:40]
                if not e.get('published_parsed') or time.mktime(e.published_parsed) < cutoff: continue
                if k in seen or t in known or not is_industry(t): continue
                seen.add(k); cand.append(dict(title=t, glink=e.link, src=e.get('source', {}).get('title', '')))
            time.sleep(1)
    print('產業報導新候選', len(cand))
    for c in cand:
        try: d = gnewsdecoder(c['glink'], interval=1); c['url'] = d.get('decoded_url') if d.get('success') else None
        except Exception: c['url'] = None
    cand = [c for c in cand if c['url'] and c['url'] not in rej_urls and c['url'] not in db and F.is_news(c['title'], c['url'])]
    cut = (dt.date.today() - dt.timedelta(days=days)).isoformat(); added = 0
    with cf.ThreadPoolExecutor(8) as ex:
        for c, (s, st, pd) in zip(cand, ex.map(lambda c: F.get_meta_summary(c['url'], c['title']), cand)):
            if not pd or s is None: continue          # 取不到原文發布日或原文打不開就不收
            if pd < cut: rejected.add(c['title']); continue
            blob = c['title'] + ' ' + s
            if SITE == 'immigrant-news': cat, unit = F.classify(c['url'], c['src'])
            elif SITE == 'hakka-news': cat, unit = '產業與觀光', F.classify(c['url'], c['src'])[1]
            else: cat, unit = F.classify(c['url'], c['src'], blob)
            if unit.startswith('www.') or '.' in unit: unit = c['src'] or unit
            db[c['url']] = dict(title=c['title'], url=c['url'], date=pd, category=cat, unit=unit, summary=s, summary_ok=False,
                                topic='產業報導', added=dt.datetime.now().strftime('%Y-%m-%d'))
            if SITE == 'hakka-news': db[c['url']]['sample'] = False
            added += 1
    json.dump(sorted(rejected), open('rejected.json', 'w'), ensure_ascii=False)
    print('產業報導新增（待寫摘要）', added, '則')
    return db

if __name__ == '__main__':
    if '--retag' in sys.argv: db = json.load(open('news_db.json'))
    else: db = fetch(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
    n = retag(db)
    json.dump(db, open('news_db.json', 'w'), ensure_ascii=False, indent=0)
    pend = [dict(url=u, title=v['title'], date=v['date'], unit=v['unit'], hint=v.get('summary', '')) for u, v in db.items() if not v.get('summary_ok')]
    json.dump(pend, open('pending_summary.json', 'w'), ensure_ascii=False, indent=1)
    print('產業報導標記', n, '則；待寫摘要', len(pend), '則')
