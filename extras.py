#!/usr/bin/env python3
"""產生 extras.js：補助資訊（讀補助王 /workspace/subsidy/補助資料庫_full.csv）與標案資訊（只讀標案王 /workspace/tender-king/raw）。
每次 deploy.sh 都會執行，讀當時最新資料。用法：python3 extras.py"""
import csv, json, glob, os, re, hashlib, datetime as dt
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.basename(os.getcwd())
SUB_CSV = '/workspace/subsidy/補助資料庫_full.csv'; TK = '/workspace/tender-king'
TODAY = dt.date.today(); TDS = TODAY.isoformat()
CFG = {
 'immigrant-news': dict(kw=['新住民','新移民','外籍配偶','外配','陸配','移工','外籍勞工','外籍看護','移民署','新二代','東南亞語'],
                        unit=['移民署','新住民']),
 'hakka-news': dict(kw=['客家','客語','客庄','客委會','浪漫台三線','台三線','義民'], unit=['客家']),
 'indigenous-news': dict(kw=['原住民','原民','部落','族語','山地鄉','原鄉','泰雅','阿美','排灣','布農','太魯閣','達悟','賽德克','卑南','魯凱','鄒族'],
                         unit=['原住民','原民']),
}[SITE]
KW, UK = CFG['kw'], CFG['unit']
OTHER = ['身心障礙','高齡者','低收入','新住民','原住民','中低收']
NEG = ['遷移工', '轉移工', '移工程', '非原住民', '非客家']
def hit(s):
    s = s or ''
    for n in NEG: s = s.replace(n, '')
    return any(k in s for k in KW)

# ---- 補助 ----
subs = []
import sys; sys.path.insert(0, '/workspace/shared-data')
try:
    import shared; _SUB = shared.load('subsidies_latest.json'); _SUB = _SUB['rows'] if _SUB else None
    _TC = shared.load('tender_cases_90d.json')
except Exception: _SUB = _TC = None
print('補助來源：' + ('共用檔' if _SUB else '補助王 CSV') + '；標案來源：' + ('共用檔' if _TC else '標案王原始檔'))
for x in (_SUB or csv.DictReader(open(SUB_CSV, encoding='utf-8-sig'))):
    if x['狀態'] == '歷史(已結束)' or x.get('資料類型') == '歷史': continue
    name, org, tgt = x['補助名稱'], x['主辦單位'], x['對象']
    ok = hit(name) or any(k in org for k in UK)
    if not ok and hit(tgt):   # 對象欄只有在「本族群」是主要對象時才算，避免通用補助（對象列一長串族群）
        others = [o for o in OTHER if o in tgt and not hit(o)]
        ok = not others
    if not ok: continue
    dl = x['截止日期'].strip(); st = x['狀態']
    if re.match(r'\d{4}-\d{2}-\d{2}$', dl) and dl < TDS: st = '已截止'
    m = re.search(r'(最高|上限|每案|補助)[^。；]{0,12}?([\d,.]+\s*(萬|億|千)?元)', x['摘要'])
    subs.append(dict(name=name, org=org, deadline=dl or '依公告', status=st, amount=m.group(0) if m else '',
                     target=tgt[:60], summary=x['摘要'][:160], url=x['原始連結'], est=x.get('預估下次開放','')))
RANK = {'開放中': 0, '即將開放': 1, '常態性/依公告': 2, '已截止': 3}
subs.sort(key=lambda s: (RANK.get(s['status'], 2), s['deadline'] if re.match(r'\d', s['deadline']) else '9999', s['name']))

# ---- 標案（只讀標案王原始資料，不更動） ----
TENDER = {'公開招標公告','公開取得報價單或企劃書公告','經公開評選或公開徵求之限制性招標公告','選擇性招標(個案)公告','公開招標更正公告','公開取得報價單或企劃書更正公告','經公開評選或公開徵求之限制性招標更正公告','限制性招標(經公開評選或公開徵求)公告'}
AWARD = {'決標公告','更正決標公告'}; FAIL = {'無法決標公告','更正無法決標公告'}
def link(x): return f"https://web.pcc.gov.tw/prkms/tender/common/noticeDate/redirectPublic?ds={x['date']}&fn={x['filename']}.xml"
def money(s):
    if not s: return None
    m = re.sub(r'[^\d]', '', s.split('元')[0]); return int(m) if m else None
def roc(s):
    m = re.match(r'(\d{2,3})/(\d{1,2})/(\d{1,2})', s or '')
    return f'{int(m[1])+1911:04d}-{int(m[2]):02d}-{int(m[3]):02d}' if m else ''
since = int((TODAY - dt.timedelta(days=90)).strftime('%Y%m%d'))
cases = {}
for f in ([] if _TC else sorted(glob.glob(TK + '/raw/day/*.json'))):
    if int(os.path.basename(f)[:8]) < since: continue
    try: recs = json.load(open(f))['records']
    except Exception: continue
    for x in recs:
        t = x['brief'].get('type'); title = x['brief'].get('title') or ''; unit = x.get('unit_name') or ''
        if t not in TENDER | AWARD | FAIL or not x.get('unit_id') or not x.get('job_number'): continue
        if not (hit(title) or any(k in unit for k in UK)): continue
        k = x['unit_id'] + '|' + x['job_number']
        c = cases.setdefault(k, dict(title=title, unit=unit, pub=0, url='', aw=0, fail=0, win=[]))
        c['title'] = title or c['title']
        d = int(x['date'])
        if t in TENDER and d >= c['pub']: c['pub'] = d; c['url'] = link(x)
        elif t in AWARD and d >= c['aw']:
            c['aw'] = d; c['aurl'] = link(x)
            nk = x['brief'].get('companies', {}).get('name_key', {})
            c['win'] = [n for n, v in nk.items() if any(q.endswith(':得標廠商') for q in v)] or c['win']
        elif t in FAIL and d >= c['fail']: c['fail'] = d; c['furl'] = link(x)
tens = []
if _TC:  # 共用檔已含明細欄位（budget/dl/amt），這裡只做本族群篩選
    cases = {k: c for k, c in _TC['cases'].items() if hit(c['title']) or any(u in c['unit'] for u in UK)}
cut60 = int((TODAY - dt.timedelta(days=60)).strftime('%Y%m%d'))
for k, c in cases.items():
    last = max(c['pub'], c['aw'], c['fail'])
    if last < cut60: continue
    budget = dl = None; amt = None
    if 'dl' in c: budget, dl, amt = c['budget'], c['dl'], c['amt']
    p = TK + '/raw/detail/' + hashlib.md5(k.encode()).hexdigest() + '.json'
    if 'dl' not in c and os.path.exists(p):
        try:
            for r in json.load(open(p))['recs']:
                budget = money(r.get('採購資料:預算金額') or r.get('已公告資料:預算金額')) or budget
                if r.get('領投開標:截止投標'): dl = roc(r['領投開標:截止投標'])
                if r.get('決標資料:總決標金額'): amt = money(r['決標資料:總決標金額'])
        except Exception: pass
    if c['aw'] and c['aw'] >= c['pub']: st, url = '已決標', c.get('aurl') or c['url']
    elif c['fail'] and c['fail'] >= c['pub']: st, url = '無法決標', c.get('furl') or c['url']
    elif dl and dl >= TDS: st, url = '招標中', c['url']
    elif dl: st, url = '已截標', c['url']
    elif c['pub'] >= int((TODAY - dt.timedelta(days=14)).strftime('%Y%m%d')): st, url = '招標中', c['url']
    else: st, url = '已截標', c['url']
    ds = str(last); tens.append(dict(title=c['title'], unit=c['unit'], budget=budget, deadline=dl or '', status=st, award=amt,
                      winner='、'.join(c['win'][:3]), date=f'{ds[:4]}-{ds[4:6]}-{ds[6:]}', url=url))
TR = {'招標中': 0, '已截標': 1, '已決標': 2, '無法決標': 3}
tens.sort(key=lambda t: (TR[t['status']], t['deadline'] if t['status'] == '招標中' else '', '' if t['status'] == '招標中' else ''.join(chr(0x10FFFF - ord(ch)) for ch in t['date'])))
tens = tens[:200]
try: tk_upd = json.load(open(TK + '/site/data/meta.json')).get('to', '')
except Exception: tk_upd = ''
open('extras.js', 'w').write('window.XSUB=' + json.dumps(subs, ensure_ascii=False) + ';\nwindow.XTEN=' + json.dumps(tens, ensure_ascii=False) +
    ';\nwindow.XUPD=' + json.dumps(dict(date=TDS, tk=str(tk_upd)), ensure_ascii=False) + ';\n')
print(f'補助資訊 {len(subs)} 筆（開放中 {sum(s["status"]=="開放中" for s in subs)}）；標案資訊 {len(tens)} 筆（招標中 {sum(t["status"]=="招標中" for t in tens)}）')
