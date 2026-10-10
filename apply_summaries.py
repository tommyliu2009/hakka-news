#!/usr/bin/env python3
"""把人工/排程寫好的摘要寫回 news_db.json。
用法: python3 apply_summaries.py summaries.json
summaries.json 格式: {"<網址>": "50～200字摘要", ...}；值寫 "REMOVE" 代表原文資訊不足，刪除並列入 rejected_urls.json。"""
import json, sys
db = json.load(open('news_db.json')); new = json.load(open(sys.argv[1]))
rej = set(json.load(open('rejected_urls.json'))); bad = []
for u, s in new.items():
    if u not in db: bad.append((u, '不在資料庫')); continue
    if s == 'REMOVE': db.pop(u); rej.add(u); continue
    s = ' '.join(s.split())
    if not 50 <= len(s) <= 200: bad.append((u, f'字數 {len(s)}')); continue
    db[u]['summary'] = s; db[u]['summary_ok'] = True
json.dump(db, open('news_db.json','w'), ensure_ascii=False, indent=0)
json.dump(sorted(rej), open('rejected_urls.json','w'), ensure_ascii=False)
pend = [dict(url=u, title=v['title'], date=v['date'], unit=v['unit'], hint=v.get('summary','')) for u, v in db.items() if not v.get('summary_ok')]
json.dump(pend, open('pending_summary.json','w'), ensure_ascii=False, indent=1)
for b in bad: print('未寫入:', *b)
print('剩待寫摘要', len(pend), '則')
