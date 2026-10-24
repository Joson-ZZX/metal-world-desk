#!/usr/bin/env python3
"""每次采集后构建每日候选选题和5页图文文案。
没有可靠中文摘要时，仅输出待复核的事实摘录和编辑建议；可选OPENAI_API_KEY强化中文初稿。
"""
from __future__ import annotations
import hashlib,json,os,re,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
from urllib.parse import urlsplit
import requests

ZH_TZ=timezone(timedelta(hours=8))
MAX_TOPICS=9
PAGES=[('封面','问题封面'),('发生了什么','事实与时间'),('核心信息','数据与证据'),('为什么重要','产业与技术联系'),('结论与互动','总结与互动')]


def cn_date(d):return d or '发布日期未确认'
def has_reviewed(r):return bool(r.get('editorial') and r.get('title_zh') and r.get('summary'))
def concise(x,max_len=180):
    s=re.sub(r'\s+',' ',str(x or '')).strip()
    return s[:max_len]+'…' if len(s)>max_len else s

def sort_recent(records,dt):
    today=dt.astimezone(ZH_TZ).date()
    filtered=[]
    for r in records:
        if r.get('source_type')=='媒体线索':continue
        date=r.get('published_at','')
        try:days=(today-datetime.strptime(date,'%Y-%m-%d').date()).days
        except (ValueError,TypeError):continue
        if -1<=days<=21:filtered.append((days,r))
    filtered.sort(key=lambda pair:(pair[0],-int(has_reviewed(pair[1])),pair[1].get('source','')))
    # Preserve category diversity: do not let all candidates become mining articles.
    chosen=[];used=set()
    for category,limit in [('全球科技产业',3),('金属与科技',2),('市场数据',2),('海外矿业',2)]:
        for days,r in filtered:
            if r['id'] in used or r.get('category')!=category:continue
            chosen.append((days,r));used.add(r['id'])
            if sum(x.get('category')==category for _,x in chosen)>=limit:break
    for days,r in filtered:
        if len(chosen)>=MAX_TOPICS:break
        if r['id'] not in used:chosen.append((days,r));used.add(r['id'])
    return sorted(chosen,key=lambda v:(v[0],-int(has_reviewed(v[1]))))[:MAX_TOPICS]

def kind(r):
    tech=(r.get('tech') or [])
    if r.get('category')=='全球科技产业':return '科技产业'
    return '、'.join(tech[:2]) if tech else '矿产与金属产业'

def fallback(r,dt):
    reviewed=has_reviewed(r)
    headline=concise(r.get('title_zh') if reviewed else r['title'],70)
    if not reviewed:headline='【译题待核】'+headline
    date=cn_date(r.get('published_at'))
    issuer=r.get('source','原始机构')
    lead=concise(r['summary'],140) if reviewed else ''
    original=concise(r.get('original_excerpt',''),180)
    # Each page contains a usable structure, specific to the record; unverified facts remain visible as original text.
    slides=[
      {'heading':headline,'body':f'全球{kind(r)}最新动态｜{issuer} · {date}','visual':'封面：主题主体图片＋短标题（素材须有使用授权）'},
      {'heading':'这次发布了什么？','body': (f'{issuer}于{date}发布有关“{concise(headline,46)}”的信息。'+((' '+lead) if reviewed else ' 目前仅取得原始标题，尚不能断言具体内容。')),'visual':'机构名称＋事件时间轴；不得把报告发布当成事件发生时间'},
      {'heading':'原始信息与证据','body': (lead if reviewed else (f'英文原文摘录（待译核）：{original}' if original else '当前没有可复核的摘要或正文，请打开原文补充事实及统计数据。')),'visual':'将原文中的重要数据画成对比图；无可靠数字则改用事实关系图'},
      {'heading':'它与哪些产业有关？','body': f'可从{kind(r)}的技术发展、产业链变化或资源需求三个角度解释此事。此页属于编辑分析，发布前须用原文及第二资料源支持判断。','visual':'建议绘制产业链关系图或变化路径图，不虚构量化关系'},
      {'heading':'可以得出什么结论？','body': f'已知事实以{issuer}原始信息为准。建议区分“已发生事项”“机构预测”和“创作者判断”，最后用一个具体问题引导讨论。','visual':'结论大字卡＋原文链接/发布日期/统计口径'}]
    return {'id':hashlib.sha256((str(dt.astimezone(ZH_TZ).date())+r['id']).encode()).hexdigest()[:16],
        'record_id':r['id'],'title':headline,'category':r.get('category','海外矿业'),
        'source':issuer,'source_title':r['title'],'published_at':r.get('published_at',''),
        'source_url':r['url'],'generated_at':dt.isoformat(timespec='seconds'),
        'mode':'人工核对摘要的模板初稿' if reviewed else '英文原文线索／待事实复核',
        'review_required':True,'ready_to_publish':False,
        'source_reviewed':reviewed,'pages':[dict(page=i+1,title=p['heading'],text=p['body'],visual=p['visual'],source_url=r['url']) for i,p in enumerate(slides)],
        'editor_note':'每页的事实、数字、时间和图片授权都需人工审核；未核对的行业影响不得作为既定结论。'}

def safe_llm_draft(r,dt,api_key,model):
    # Send only source data, never invent background numbers or prompt that encourages speculation.
    evidence={'title_en':r['title'],'title_zh_reviewed':r.get('title_zh','') if has_reviewed(r) else '',
              'issuer':r['source'],'date':r.get('published_at',''),'source':r['url'],
              'verified_cn_summary':r.get('summary','') if has_reviewed(r) else '',
              'original_excerpt_unverified':r.get('original_excerpt','')[:850],
              'category':r.get('category',''),'metals':r.get('metals',[]),'tech':r.get('tech',[])}
    system='''你是严谨的中文科技与矿业信息编辑。你的所有事实必须严格来自用户提供的证据字段。仅有标题时，不得编造事件细节、数字、影响或结论。
生成一个有趣但克制的中文微信贴图创作初稿，包含总标题及5页完整短文案。每页标题至多20字，正文至多110汉字。区分已发生事实、推断和未来计划。
没有依据时明确写“待原文核实”，不得填补。每页设计一条配图建议。不要引用用户未给的来源，不准额外引入统计数字。
严格仅返回JSON对象：{"title":"...","pages":[{"title":"...","text":"...","visual":"..."}*5]}。'''
    resp=requests.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':'Bearer '+api_key},json={
        'model':model,'temperature':0.1,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(evidence,ensure_ascii=False)}]},timeout=45)
    resp.raise_for_status();data=resp.json();draft=json.loads(data['choices'][0]['message']['content'])
    if len(draft.get('pages',[]))!=5 or not all(x.get('title') and x.get('text') and x.get('visual') for x in draft['pages']):
        raise ValueError('AI输出不符合5页结构')
    result=fallback(r,dt);result['title']=concise(draft.get('title'),80)
    result['pages']=[{'page':i+1,'title':concise(s['title'],40),'text':concise(s['text'],210),'visual':concise(s['visual'],150),'source_url':r['url']} for i,s in enumerate(draft['pages'])]
    result['mode']='AI来源约束的中文初稿（待人工复核）';result['editor_note']='AI可出错；即使来源于官方标题或摘要，也应逐页核查原文后再发布。'
    return result

def generate_daily_briefs(records,dt,data_dir):
    selected=sort_recent(records,dt)
    editorial_file=Path(data_dir)/'editorial_library.json'
    try:editorial=json.loads(editorial_file.read_text('utf-8'))
    except (FileNotFoundError,ValueError):editorial={}
    key=os.environ.get('OPENAI_API_KEY','').strip();model=os.environ.get('OPENAI_MODEL','gpt-4.1-mini')
    topics=[];ai_success=0;ai_fail=0
    for days,r in selected:
        if r.get('url') in editorial:
            t=fallback(r,dt);curated=editorial[r['url']]
            t['title']=curated['title'];t['pages']=[dict(page=i+1,title=p['title'],text=p['text'],visual=p['visual'],source_url=r['url']) for i,p in enumerate(curated['pages'])]
            t['mode']='人工核对来源的示范初稿（发布前仍需审核）'
            t['editor_note']='已按来源整理成中文初稿；请在发布前再次检查事件数据、来源链接和配图授权。'
        elif key:
            try:
                t=safe_llm_draft(r,dt,key,model);ai_success+=1
            except Exception as e:
                ai_fail+=1;print('AI generation failed',r.get('id'),str(e)[:120],file=sys.stderr)
                t=fallback(r,dt)
        else:t=fallback(r,dt)
        t['age_days']=days;topics.append(t)
    out={'for_date':dt.astimezone(ZH_TZ).strftime('%Y-%m-%d'),'generated_at':dt.isoformat(timespec='seconds'),
       'selection_window_days':21,'new_today_count':sum(t['age_days']==0 for t in topics),
       'source_count':len(topics),'llm_enabled':bool(key),'llm_success':ai_success,'llm_failed':ai_fail,
       'topics':topics, 'notice':'每日自动刷新候选。无新信息时显示近21日资料，不标为今日新发；文案全部需要人工核实后才能发布。'}
    (Path(data_dir)/'daily_briefs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return out

if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent
    records=json.loads((root/'data/records.json').read_text('utf-8'))
    obj=generate_daily_briefs(records,datetime.now(timezone.utc),root/'data')
    print('Generated',len(obj['topics']),'daily topics for',obj['for_date'],'AI',obj['llm_enabled'])
