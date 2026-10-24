"""Offline end-to-end regression tests. No internet and no API key needed."""
from __future__ import annotations
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import update

DATE=datetime(2026,10,24,3,0,tzinfo=timezone.utc)
RSS='''<?xml version="1.0"?><rss version="2.0"><channel><title>Example Feed</title><item><title>Researchers improve AI robotics batteries</title><link>https://news.mit.edu/2026/robotics-battery-research-1024</link><pubDate>Sat, 24 Oct 2026 11:00:00 GMT</pubDate><description>Researchers demonstrated a robotics battery prototype in testing.</description></item></channel></rss>'''
HTML='''<!doctype html><html><head></head><body><article><h2><a href="https://investor.asml.com/news-releases/news-release-details/asml-introduces-chip-fabrication-technology">ASML introduces advanced chip fabrication technology</a></h2><time datetime="2026-10-23">23 October 2026</time><p>Technology announcement.</p></article></body></html>'''

class FakeResponse:
    def __init__(self,text):self.content=text.encode('utf-8');self.text=text;self.url='https://investor.asml.com/news/press-releases'

mit={'id':'test-mit','name':'MIT','institution':'MIT News','url':'https://news.mit.edu/rss','host':'news.mit.edu','path':'/','type':'rss','tier':'科研机构','focus':'tech'}
asml={'id':'test-asml','name':'ASML','institution':'ASML','url':'https://investor.asml.com/news/press-releases','host':'investor.asml.com','path':'/news-releases/news-release-details/','type':'html','tier':'企业公告','focus':'tech','always_relevant':True}

# RSS/HTML parsing (no requests)
with patch.object(update,'fetch',return_value=FakeResponse(RSS)):
    items=update.list_rss(mit)
    assert len(items)==1 and items[0]['published_at']=='2026-10-24'
    assert items[0]['category']=='全球科技产业'
with patch.object(update,'fetch',return_value=FakeResponse(HTML)):
    items_html=update.list_html(asml)
    assert len(items_html)==1 and items_html[0]['published_at']=='2026-10-23'

# Full update pipeline and daily topic bundling (no requests)
with tempfile.TemporaryDirectory() as temp:
    folder=Path(temp)
    with patch.object(update,'DATA',folder),patch.object(update,'NOW',DATE),patch.object(update,'SOURCES',[mit]),patch.object(update,'list_rss',return_value=items),patch.object(update,'price_data',side_effect=ValueError('price source unreachable')),patch.object(update.time,'sleep',return_value=None):
        update.run()
        assert (folder/'daily_briefs.json').is_file()
        payload=json.loads((folder/'dashboard-data.js').read_text('utf-8').split('=',1)[1].strip().rstrip(';'))
        assert len(payload['records'])==1
        assert len(payload['daily_briefs']['topics'])==1
        assert len(payload['daily_briefs']['topics'][0]['pages'])==5
        assert payload['daily_briefs']['topics'][0]['ready_to_publish'] is False
        assert payload['status']['sources'][0]['state']=='success'
    # Failure must preserve prior data
    with patch.object(update,'DATA',folder),patch.object(update,'NOW',DATE),patch.object(update,'SOURCES',[mit]),patch.object(update,'list_rss',side_effect=RuntimeError('site temporary failure')),patch.object(update,'price_data',side_effect=ValueError('price source unreachable')),patch.object(update.time,'sleep',return_value=None):
        update.run()
        assert len(json.loads((folder/'records.json').read_text('utf-8')))==1
        assert json.loads((folder/'status.json').read_text('utf-8'))['sources'][0]['state']=='failed'

print('PASS: RSS + HTML parsing, update + five-page draft bundling, offline failure retention')
