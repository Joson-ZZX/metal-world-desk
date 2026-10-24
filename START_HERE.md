# 金属与世界｜上线操作单（V3）

## 当前状态（2026-10-24）

- 本地预览：已验证网页数据快照可读取；采集脚本和5页选题自动打包已通过离线端到端测试。
- 官方来源已预设：IEA、USGS、ICSG、BHP、Rio Tinto、MIT News、SIA、ASML、TSMC及MINING.COM（媒体线索）。部分来源可能限制爬虫；真实成功率必须在联网环境测试。
- 世界银行价格：使用官方**月度**工作簿；目前内置样本价格为0，不能当作实时行情。
- 未完成：创建GitHub仓库、实际联网抓取、公开网址部署、连续三天定时运行。不要把本地快照称作实时网站。

## 最简上线方式

**1. 创建GitHub仓库（此操作须由账户持有人完成）**

打开 https://github.com/new ，在自己的账号下新建仓库：
- Repository name: `metal-world-desk`
- Visibility: `Public`（GitHub Free的Pages适用于公开仓库；不要上传私有或商业保密资料）
- 勾选 `Add a README file`，点击 `Create repository`

创建后将完整仓库地址交给协作助手，就可以在已授权的GitHub连接许可范围内协助上传、调试仓库文件。若不使用连接器，也可自行上传本部署包中 `metal-world-platform` 内的所有文件，包括隐藏目录 `.github`。

**2. 启用 GitHub Pages**

仓库 `Settings` → `Pages` → `Build and deployment` → `Source` 选择 `GitHub Actions`。如显示组织安全策略，请按仓库账户设置操作。

**3. 首次运行（验证真实数据）**

仓库 `Actions` → `Metal World Daily Update` → `Run workflow`。
检查日志中 `source_success`；若为0，说明实际源站采集仍未成功，不能判断已联网正常。

**4. 检查线上页面**

仓库 `Settings` → `Pages` 查看 GitHub 提供的网址。首次访问重点打开：`全球信息流`、`全球科技产业`、`每日贴图工作台`、`信息来源与监测`。

**5. 连续运行三天**

每天北京时间07:20计划触发。GitHub定时任务可能延迟或暂停，请每天检查页面的采集时间与 `Actions` 实际执行记录。如果源站反爬或HTML调整，失败会标示异常，并保留上次信息。

## 可直接测试的程序

```bash
python -m pip install -r requirements.txt
python scripts/test_pipeline.py
python scripts/test_daily.py
python scripts/validate.py
python scripts/update.py
```

前三条是**离线测试**；第四条才会联网尝试采集。再次运行验证命令 `python scripts/validate.py`。项目内 `update_now.bat` 可用于Windows手动运行。

## 每日完整中文贴图的边界

- **无API密钥：** 自动得到选题＋5页结构＋原始来源。对于未核实的英文摘要，页面只提供待核查稿，不伪造完整中文新闻。
- **可选配置API密钥：** 仓库 `Settings → Secrets and variables → Actions → New repository secret` 中填写 `OPENAI_API_KEY`（需要单独开通API及计费），可生成更多中文5页初稿。所有输出仍必须人工复核。
- 平台只生成文本，不会自动生成5张图片，也不能自动在微信发布。

**本V3修复：** `update.py`在采集后会调用选题生成，且网页数据打包包含 `daily_briefs`。修正了以前采集后网页贴图池不更新的问题；新增了源站文章日期缺失时的有限详情页解析、TSMC与ASML源、离线回归测试，以及规范化GitHub Pages工作流。
