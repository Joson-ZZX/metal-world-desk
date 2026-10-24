"""将人工核验后的 JSON 重新打包进可离线浏览的数据JS。"""
import json
from pathlib import Path
D=Path(__file__).resolve().parent.parent/'data'
blob={k:json.loads((D/(file+'.json')).read_text('utf-8')) for k,file in [('records','records'),('prices','prices'),('status','status'),('daily_briefs','daily_briefs')]}
(D/'dashboard-data.js').write_text('window.METAL_WORLD_DATA = '+json.dumps(blob,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
print('Updated dashboard-data.js:',len(blob['records']),'records')
