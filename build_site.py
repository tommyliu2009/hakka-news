#!/usr/bin/env python3
"""由 news_db.json 產生 data.js。只輸出已有合格摘要（summary_ok 且 50～200 字）的項目。"""
import json
import sys

CATS = ['客家文化', '客庄新聞', '客語推廣', '節慶活動', '產業與觀光', '全球客家', '政策與補助']
db = json.load(open('news_db.json'))
st = json.load(open('source_status.json'))
items = []
skipped = 0
for key, v in db.items():
    if not v.get('summary_ok'):
        skipped += 1
        continue
    summary = v.get('summary', '')
    if not 50 <= len(summary) <= 200:
        print('略過字數不符', v.get('title'), len(summary))
        skipped += 1
        continue
    if v.get('category') not in CATS:
        sys.exit('欄目不在網站分類：' + v.get('title', key))
    if v.get('sample') and ('【範例】' not in v.get('title', '') or '範例' not in summary):
        sys.exit('範例稿缺少標示：' + v.get('title', key))
    id_ = v.get('id') or key
    item = {
        'id': id_,
        'title': v['title'],
        'date': v['date'],
        'category': v['category'],
        'unit': v['unit'],
        'summary': summary,
        'sample': bool(v.get('sample')),
        'url': v.get('url') or ('article.html#' + id_),
    }
    if item['sample']:
        item['url'] = 'article.html#' + id_
    items.append(item)
items.sort(key=lambda v: (v['date'], v['id']), reverse=True)
open('data.js', 'w').write(
    'window.NEWS=' + json.dumps(items, ensure_ascii=False) + ';\n'
    'window.UPDATED=' + json.dumps(st['updated'], ensure_ascii=False) + ';\n'
)
print('網站資料', len(items), '則；未上線', skipped, '則')
