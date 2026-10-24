"""离线回归测试：候选筛选、日期窗口、多主题分类与五页结构。"""
import json,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from daily_briefs import sort_recent,generate_daily_briefs,fallback
root=Path(__file__).resolve().parent.parent
records=json.loads((root/'data/records.json').read_text('utf-8'))
fixed=datetime(2026,10,24,tzinfo=timezone.utc)
picked=sort_recent(records,fixed)
assert picked and len(picked)<=9
assert any(x['category']=='全球科技产业' for _,x in picked)
assert all((fixed.date()-datetime.strptime(x['published_at'],'%Y-%m-%d').date()).days<=21 for _,x in picked)
with tempfile.TemporaryDirectory() as d:
    result=generate_daily_briefs(records,fixed,Path(d))
    assert len(result['topics'])==len(picked)
    assert all(len(t['pages'])==5 and not t['ready_to_publish'] for t in result['topics'])
    assert result['new_today_count']==0
    assert any('人工核对来源' in t['mode'] for t in result['topics']) is False # no editorial sample file in temp
    x=fallback({'id':'x','title':'Robotics technology announcement','url':'https://example.org/robot','published_at':'2026-10-23','source':'TEST','source_type':'科研机构','category':'全球科技产业','original_excerpt':'New robot model demonstrated.'},fixed)
    assert '尚不能断言具体内容' in x['pages'][1]['text']
print('TEST PASS daily logic',len(picked),'topics')
