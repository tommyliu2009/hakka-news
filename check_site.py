#!/usr/bin/env python3
"""檢查展示站：範例標示、欄目、頁面與 Python 語法。"""
import json, pathlib, py_compile, re, sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
CATS = ['客家文化', '客庄新聞', '客語推廣', '節慶活動', '產業與觀光', '全球客家', '政策與補助']
PAGES = ['index.html', 'about.html', 'organization.html', 'accessibility.html', 'article.html', '404.html']
NEED = ['跳至主要內容', '客家全球新聞網', '展示版本', '本站不是客家委員會']
# 只列簡體專用字，不含臺繁也用的「件、信、用、量」等。
SIMPLIFIED = set('国发这时间后还对从说们长门东车电话广报业产实现关开问题应该样进动员团书写让给经济软网络视频认户质')

class Probe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.skip = False
        self.main = False
        self.lang = False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'html' and str(d.get('lang', '')).startswith('zh-Hant'):
            self.lang = True
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a' and d.get('href') == '#main':
            self.skip = True
        if tag == 'main':
            self.main = True

def main():
    for name in ['sample_articles.py', 'build_site.py', 'fetch_news.py', 'apply_summaries.py', 'pubdate.py']:
        py_compile.compile(str(ROOT / name), doraise=True)
    db = json.loads((ROOT / 'news_db.json').read_text())
    data = (ROOT / 'data.js').read_text()
    if 'window.NEWS=' not in data or 'window.UPDATED=' not in data:
        sys.exit('data.js 格式不對')
    if len(db) < 28:
        sys.exit('範例稿不足')
    counts = {c: 0 for c in CATS}
    for key, v in db.items():
        if not v.get('sample') or not v.get('summary_ok'):
            sys.exit('展示資料庫應全部是已完成的範例：' + key)
        if not v['title'].startswith('【範例】') or '範例' not in v['summary']:
            sys.exit('缺少範例標示：' + key)
        if v['category'] not in CATS:
            sys.exit('欄目錯誤：' + key)
        if not 50 <= len(v['summary']) <= 200:
            sys.exit('字數錯誤：' + key)
        if any(ch in v['title'] + v['summary'] for ch in '「」『』'):
            sys.exit('範例稿含引號：' + key)
        counts[v['category']] += 1
    if any(n < 4 for n in counts.values()):
        sys.exit('有欄目少於 4 則：' + str(counts))
    for name in PAGES:
        text = (ROOT / name).read_text()
        bad = [ch for ch in SIMPLIFIED if ch in text]
        if bad:
            sys.exit(name + ' 含簡體字元：' + ''.join(bad))
        probe = Probe()
        probe.feed(text)
        if not probe.lang or not probe.skip or not probe.main or probe.h1 < 1:
            sys.exit(name + ' 缺少語系、跳至內容、main 或 h1')
        if name != '404.html':
            for phrase in NEED:
                if phrase not in text:
                    sys.exit(name + ' 缺少：' + phrase)
    js = (ROOT / 'app.js').read_text() + (ROOT / 'site.js').read_text()
    for c in CATS:
        if c not in js:
            sys.exit('腳本缺少欄目 ' + c)
    print('檢查通過', len(db), '則', counts)

if __name__ == '__main__':
    main()
