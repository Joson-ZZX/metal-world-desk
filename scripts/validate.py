"""重要校验：禁止未来发布日期、伪造价格周期、无来源链接。"""
import json
from datetime import datetime, timedelta,timezone
from pathlib import Path
from urllib.parse import urlsplit
root=Path(__file__).resolve().parent.parent/'data'
records=json.loads((root/'records.json').read_text('utf-8'))
prices=json.loads((root/'prices.json').read_text('utf-8'))
assert isinstance(records,list)
ids=set();today=datetime.now(timezone.utc).date()
for r in records:
    assert r['id'] not in ids, 'Duplicate ID'
    ids.add(r['id'])
    assert urlsplit(r['url']).scheme == 'https',r['url']
    if r.get('published_at'):
        assert datetime.strptime(r['published_at'],'%Y-%m-%d').date() <= today+timedelta(days=1),r
assert prices.get('not_realtime',True) is True
for r in prices.get('series',[]):
    assert r['unit'] and r['source_url'] and r['month'] and isinstance(r['value'],(int,float))
drafts=json.loads((root/'daily_briefs.json').read_text('utf-8'))
assert isinstance(drafts.get('topics'),list)
for t in drafts['topics']:
    assert urlsplit(t['source_url']).scheme == 'https'
    assert len(t['pages'])==5
    assert t['review_required'] is True and t['ready_to_publish'] is False
    for i,page in enumerate(t['pages']):
        assert page['page']==i+1 and page['title'] and page['text'] and page['visual']
        assert page['source_url']==t['source_url']
print('DRAFTS VALIDATION PASS',len(drafts['topics']),'topics')
print('VALIDATION PASS' ,len(records),'records',len(prices.get('series',[])),'price rows')
