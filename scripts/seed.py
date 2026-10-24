"""首次可离线浏览的官方公开信息样本；所有条目由2026-10-24公开资料核对，非实时抓取。"""
import json, hashlib
from pathlib import Path
D=Path(__file__).resolve().parent.parent/'data'
rows=[
('2026-10-14','SIA','产业协会','全球科技产业','SIA Applauds GlobalFoundries Expansion Under U.S.-Japan Initiative','SIA披露GlobalFoundries参与美国纽约州半导体新工厂计划','SIA在2026年10月14日新闻稿中介绍GlobalFoundries将在美国纽约州Malta运营两座新半导体制造设施。项目仍有建设实施安排，不应视为已投产。','https://www.semiconductors.org/sia-applauds-globalfoundries-expansion-under-u-s-japan-initiative/',[],['半导体','先进制造']),
('2026-10-07','MIT News','科研机构','全球科技产业','Planning system ensures a robot’s flight path will remain collision-free','MIT研究团队提出无人机动态避障轨迹规划方法SANDO','MIT News介绍了SANDO轨迹规划方法：在未知、动态障碍物环境中构建安全飞行路径。研究人员报告了仿真验证和12次真实无人机试飞；不等于所有实际环境都已商业部署。','https://news.mit.edu/2026/planning-system-ensures-robots-flight-path-will-remain-collision-free-1007',[],['机器人','AI与算力']),
('2026-10-05','SIA','产业协会','全球科技产业','Year-to-Date Global Semiconductor Sales Top $1 Trillion Through August','SIA：2026年8月全球半导体月销售额1597亿美元','美国半导体行业协会10月5日援引WSTS统计称，2026年8月全球半导体销售额为1597亿美元，同比增长144.3%。该月度统计采用三个月移动平均口径；全年累计已超过1万亿美元。','https://www.semiconductors.org/year-to-date-global-semiconductor-sales-top-1-trillion-through-august/',[],['半导体']),
('2026-10-23','ICSG','一手机构','市场数据','ICSG October 2026 Monthly Press Release','ICSG发布2026年10月铜市场月度新闻稿','国际铜研究组官网列示了2026年10月23日的月度新闻稿。具体统计数值应以附件原文为准。','https://icsg.org/press-releases/',['铜'],[]),
('2026-10-20','BHP','企业公告','海外矿业','BHP Operational review for the quarter ended 30 September 2026','必和必拓发布2026年第三季度运营回顾','BHP指出，该季度铜产量受计划内品位下降、设备检修和临时干扰影响，持续推进铜与钾肥项目。','https://www.bhp.com/news/media-centre/releases/2026/10/bhp-operational-review-for-the-quarter-ended-30-september-2026',['铜'],['AI/数据中心']),
('2026-10-14','IEA','一手机构','金属与科技','Powering Artificial Intelligence: Strategies for integrating data centres into electricity systems','IEA发布《为人工智能供电》专题报告','IEA研究数据中心投资增长对电网、电价、环境和水资源的影响，覆盖34个政策辖区。内容适合结合铜、电网和AI基础设施开展原创解读。','https://www.iea.org/reports/powering-artificial-intelligence',['铜'],['AI/数据中心']),
('2026-10-14','ICSG','一手机构','市场数据','ICSG Copper Market Forecast 2026–2027','ICSG发布2026—2027年铜市场预测','国际铜研究组更新全球铜矿与精炼铜市场预测，涵盖产量、消费和供需平衡。引用具体盈余或缺口数字前请查阅原始PDF及统计口径。','https://icsg.org/download/2026-10-14-press-release-icsg-copper-market-forecast-2026-2027/',['铜'],[]),
('2026-10-01','Rio Tinto','企业公告','海外矿业','Rio Tinto and governments secure the future of Bell Bay Aluminium until 2031','力拓与澳大利亚政府机构达成协议，支持Bell Bay铝厂运营至2031年','力拓宣布与塔斯马尼亚州及澳大利亚联邦政府达成协议，为Bell Bay铝厂运营至2031年底提供支持，并延续相应电力供应安排。','https://www.riotinto.com/en/news/releases/2026/rio-tinto-tasmanian-government-and-commonwealth-government-secure-the-future-of-bell-bay-aluminium-until-2031',['铝'],[]),
('2026-09-29','USGS','一手机构','海外矿业','USGS Updates U.S. Critical Mineral Deposits','USGS更新美国关键矿产矿床数据库：涉及1271处已知矿床','USGS公开资料显示，其更新数据库收录美国41州及波多黎各的1271处已知关键矿产矿床，其中412处有资源记录但没有生产历史。','https://www.usgs.gov/news/national-news-release/usgs-updates-us-critical-mineral-deposits',['关键矿产'],[]),
('2026-09-10','Rio Tinto','企业公告','海外矿业','Nyangumarta Warrarn Aboriginal Corporation and Rio Tinto sign milestone agreement for Winu Project','力拓就澳大利亚Winu铜金矿项目签署重要项目协议','力拓宣布与相关原住民组织就拟开发的Winu铜金矿项目签署项目协议，属于项目开发进展信息，不等同于已经投产。','https://www.riotinto.com/en/news/releases',['铜'],[]),
('2026-07-16','IEA','一手机构','金属与科技','Global Critical Minerals Outlook 2026','IEA发布《2026年全球关键矿产展望》','报告评估全球关键矿产市场、投资、技术及供需趋势，并讨论人工智能、数字系统和先进制造产业所面临的矿产供应链问题。','https://www.iea.org/reports/global-critical-minerals-outlook-2026',['铜','锂','镍','稀土'],['AI/数据中心','新能源']),
('2026-08-18','BHP','企业公告','市场数据','BHP Results for the full year ended 30 June 2026','BHP发布2026财年全年业绩','BHP披露2026财年铜产量约200万吨，强调铜业务在集团经营及增长布局中的重要性。其财年截止日为6月30日，不应等同于2026自然年。','https://www.bhp.com/news/media-centre/releases/2026/08/bhp-results-for-the-full-year-ended-30-june-2026',['铜'],[]),
]
items=[]
for date,src,stype,cat,title,cn,summary,url,metal,tech in rows:
 items.append({'id':hashlib.sha256(url.encode()).hexdigest()[:16],'title':title,'title_zh':cn,'url':url,'source':src,'source_name':src,'source_type':stype,'published_at':date,'fetched_at':'','summary':summary,'original_excerpt':'','category':cat,'metals':metal,'tech':tech,'verification':'已核对官方公开信息（2026-10-24）','editorial':True})
items.sort(key=lambda x:x['published_at'],reverse=True)
(D/'records.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n','utf-8')
(D/'prices.json').write_text(json.dumps({'not_realtime':True,'series':[],'notice':'等待首次联网下载世行官方月度数据；不填充模拟价格。'},ensure_ascii=False,indent=2)+'\n','utf-8')
# Source list is fixed authoritative entry points; matches update.py
links=[
 {'name':'世界银行 · Pink Sheet（月度价格）','url':'https://www.worldbank.org/en/research/commodity-markets','frequency':'每月','detail':'历史月度价格，非即时行情'},
 {'name':'IEA · 2026关键矿产展望','url':'https://www.iea.org/reports/global-critical-minerals-outlook-2026','frequency':'年度/专题','detail':'全球关键矿产供需、投资、供应链'},
 {'name':'USGS · 矿产统计','url':'https://www.usgs.gov/centers/national-minerals-information-center/mineral-commodity-summaries','frequency':'年度','detail':'全球主要矿种产量、资源储量'},
 {'name':'ICSG · 铜业统计','url':'https://icsg.org/selected-copper-statistics/','frequency':'月度/预测','detail':'铜矿及精炼铜供需和预测'},
 {'name':'LME · 官方金属价格','url':'https://www.lme.com/en/market-data/reports-and-data/lme-official-prices','frequency':'依许可','detail':'访问与使用授权受限，本平台不展示未授权实时行情'},
 {'name':'Rio Tinto · 公司公告','url':'https://www.riotinto.com/en/news/releases','frequency':'按公告','detail':'矿山项目与生产经营信息'},
 {'name':'SIA · 半导体产业','url':'https://www.semiconductors.org/news-events/latest-news/','frequency':'公告/统计','detail':'SIA半导体市场销售统计、制造能力和产业链新闻'},
 {'name':'MIT News · 科技研究','url':'https://news.mit.edu/rss','frequency':'持续更新','detail':'MIT科技研究进展，覆盖AI、机器人、先进材料等'},
 {'name':'IEA · AI与能源','url':'https://www.iea.org/reports/powering-artificial-intelligence','frequency':'专题','detail':'数据中心、AI与电网供需'},
 {'name':'BHP · 交易所公告','url':'https://www.bhp.com/investor-centre/market-announcements','frequency':'按公告','detail':'业绩、矿山项目及生产经营披露'},
]
status={'attempted_at':None,'timezone':'Asia/Singapore','new_records':0,'record_count':len(items),'sources':[], 'official_links':links,'note':'2026-10-24已核实公开样本；首次联网执行自动更新后开始记录采集结果。'}
(D/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n','utf-8')
(D/'dashboard-data.js').write_text('window.METAL_WORLD_DATA = '+json.dumps({'records':items,'prices':{'not_realtime':True,'series':[]},'status':status},ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
print('seeded',len(items),'official entries')
