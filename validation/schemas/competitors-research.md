# 竞品公开资料检索（A3.1）

**任务**：任务 18 [A3.1] 竞品公开资料检索
**执行者**：竞品分析专家（Agent）
**检索日期**：2026-10-25
**产出定位**：本文件是 `competitors.csv` 的**公开资料输入源**，不是最终对比表。最终对比表由任务 19 [A3.2] 汇总任务 6/7（H3.1/H3.2 真人实操）与本文件后产出。

> **硬约束声明**
> 1. 本文件所有结论均附 `source_url`。无公开资料可支撑的字段一律写 `unknown`，并在 `notes` 标注「需实操验证」。
> 2. **本文件不含 `satisfaction_score` 数据**。M10（现有平台满意度）是低优指标，必须由创始人真人实操（tasks.md 任务 6 [H3.1] / 任务 7 [H3.2]）填写，本任务不得凭空打分。每一行 `notes` 均已重申。
> 3. 平台的**真实搜索体验**（实际能搜出多少岗位、标签是否真的可点开、投递链路是否通）无法通过资料检索获得，全部移交任务 6/7。
> 4. 「官方自述」与「第三方报道」在 `notes` 中分别标注（`[官方]` / `[第三方]` / `[索引]`）。

---

## 1. 检索方法说明

### 1.1 使用的检索工具

- `WebSearch`：9 组关键词（中文 1 组、英文 8 组）
- `WebFetch`：对关键平台做**首页/定价页/说明页直接抓取核实**（共 12 次成功抓取）
- `curl`：对 6 个域名做存活与 HTTP 状态码核验（不跟随重定向，取最终状态）

### 1.2 使用的检索关键词

| # | 关键词 | 目标 |
|---|---|---|
| 1 | `AI agent developer job board dedicated hiring agents` | 一类：Agent 垂直平台 |
| 2 | `"AI agent" jobs board specialized job board for AI engineers 2026` | 一类 + 三类 |
| 3 | `ai-jobs.net AI jobs board LLM machine learning` | 一类 |
| 4 | `Honeypot AI jobs board applied AI engineers` | 二类/三类对照 |
| 5 | `LinkedIn "AI Agent" skill tags job search filter` | 二类 |
| 6 | `Indeed Glassdoor ZipRecruiter AI agent jobs filter skills 2026` | 二类 |
| 7 | `Wellfound AngelList AI agent engineer jobs remote startup 2026` | 三类 |
| 8 | `Remote OK We Work Remotely AI jobs category LLM agent filter` | 三类 |
| 9 | `Hacker News "Who is hiring" AI agent engineer 2026 thread` | 三类 |
| 10 | `AIJobs.ai pricing post a job AI-only job board cost` | 一类定价 |
| 11 | `"Welcome to the Jungle" OR "Stack Overflow Jobs" AI machine learning jobs category filter` | 三类 |
| 12 | `Foorilla ai-jobs.net AI job board pricing employer post job cost` | 一类（ai-jobs.net 迁移核实） |
| 13 | `Hugging Face jobs YC Work at a Startup AI agent engineer listing` | 三类 |
| 14 | `"agent jobs" OR "agentjobs" job board AI agent developers 2026 launch` | 一类 + 域名冲突排查 |
| 15 | `LinkedIn official jobs AI agent skill filter recruiter search "AI Agent" 2026` | 二类 |
| 16 | `BOSS直聘 脉脉 AI Agent 岗位 专区 智能体 招聘 2026` | 二类（中国市场） |
| 17 | `Arc.dev Braintrust Toptal Contra AI engineer remote jobs 2026` | 三类 |
| 18 | `We Work Remotely AI machine learning category job board 2026 pricing $299` | 三类 |
| 19 | `80000 Hours Built In AI jobs category machine learning filter 2026` | 三类 |
| 20 | `Indeed "AI jobs" hub category filter site:indeed.com OR Glassdoor AI careers job search filters official` | 二类 |

### 1.3 检索了什么

- 三类平台的存在性与定位（**一类**：AI/Agent 垂直招聘平台；**二类**：通用招聘平台；**三类**：技术招聘平台）
- 每个平台的：岗位是否覆盖 AI Agent 类、技能标签支持粒度、定价模式（公开则记录）
- 特别核实项：是否存在**自称有「AI Agent 岗位专区」**的平台，并区分官方自述与第三方报道
- 域名冲突排查：`agentjobs.com` / `agentjobs.io`（与本项目名同名）
- 存量平台存活核实：Stack Overflow Jobs、Kaggle Jobs、Papers With Code、Hired、Triplebyte、Otta

### 1.4 CSV 并入说明（供任务 19）

本文档含 **3 张表，列名完全一致**，按「一 / 二 / 三」顺序纵向拼接即为可解析 CSV。共 **36 行平台记录**：一类（AI/Agent 垂直）16 行、二类（通用平台）6 行、三类（技术平台）14 行。

| 本文件列 | competitors.csv 对应列 | 映射说明 |
|---|---|---|
| `platform` | `platform` | 直接映射 |
| `positioning` | （无对应） | 作为 `job_types_covered` 的补充说明，不直接并入 |
| `target_users` | （无对应） | 任务 19 可并入 `differentiation` 或丢弃 |
| `agent_job_availability` | `agent_job_availability` | 直接映射；本文件用 `yes/partial/no/unknown` 受控值 |
| `skill_tag_support` | `skill_tag_support` | 直接映射；本文件用 `yes/partial/no/unknown` 受控值 |
| `pricing` | （无对应） | 可并入 `differentiation` 作为商业化证据 |
| `source_url` | `evidence_url` | 直接映射（competitors.csv 允许多 URL 时用 `;` 分隔） |
| `notes` | （无对应） | 供任务 19 判定证据强度与是否需实操补充 |

> `differentiation` 列由任务 19 统一维护**受控词表**后填写；本文件不预填，避免去重失效。
> `satisfaction_score` 列本文件**不产出**，留给任务 6/7 真人实操。

---

## 2. 发现清单表

### 2.1 第一类：AI / Agent 垂直招聘平台

| platform | positioning | target_users | agent_job_availability | skill_tag_support | pricing | source_url | notes |
|---|---|---|---|---|---|---|---|
| Agentic Engineering Jobs (agenticengineeringjobs.com) | 「面向构建 agentic 系统的工程师的垂直招聘板」，7 类岗位分类法 | AI Agent 工程师、Agent 架构师、AgentOps、Agentic Workflow、Agent PM、Prompt/LLM 工程师 | yes | partial | unknown | https://agenticengineeringjobs.com/llm-info | [官方] 官方页自述 7 类岗位分类法并按岗位公布薪资带；仅提供关键词+角色+remote 筛选，**未见 LangChain/LangGraph/MCP 等技能标签体系**（列表里只出现 angular/frontend/fintech 等偶发标签）；有「Post a job」入口但未公示价格。首页自述 200 个在招 agentic 岗位。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Agentic Engineering Jobs (agentic-engineering-jobs.com) | 「为构建 agentic 系统的人提供的招聘板」 | agentic AI 工程师（全球/远程），含 LangGraph/CrewAI/Pydantic AI 栈使用者 | yes | yes | free（官方自述） | https://agentic-engineering-jobs.com/about | [官方] 由 Maxim Buz（Heazy Studio）运营；agentic-stack 筛选明确列出 LangGraph、CrewAI、Pydantic AI、RAG、multi-agent、LLM observability、evals；官方称 500+ 在招、无付费墙。但另有[索引]来源称其已改为 $150/单条 60 天 + $49 置顶 + $2,990/年包年（https://agentic-engineering-jobs.com/employers 直接抓取返回 404，无法复核），**定价存在冲突，需实操验证**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| AgenticCareers (agenticcareers.co) | 面向 agentic AI 劳动力市场的专门市场，发布 agentic 岗位的开放数据集（CC BY 4.0） | Agent builder / operator / trainer，AI Agent 工程师、Agentic Systems Architect、LLM Ops Lead | yes | partial | unknown | https://agenticcareers.co/state-of-agentic-hiring | [官方] 自述追踪 14 个来源共 2,962 个在招岗位、890 家公司，30 天内新增 2,065；AI Agent Engineer 占 15.3%；39% 岗位披露薪酬，披露样本中位数 $236,350；提供 Jobs/Companies/Roles 索引与角色类别、资历、薪酬披露、远程、新鲜度、雇主段位等分面，以及公司阶段与栈筛选。价格未公示。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| AI Native Builder (ai-native-builder.com/ai-agent-jobs) | 「面向设计 tool-using agents、LLM 应用、多智能体工作流、评测与生产级 agent 系统的工程师与构建者的 AI agent 岗位板」 | AI agent 工程师、agentic coding 开发者 | yes | yes | unknown | https://www.ai-native-builder.com/ai-agent-jobs | [官方] 页面标注 300 个在招岗位（其中 77 个远程），更新于 2026-10-24；岗位标签含 AI Agents / Agentic Coding / No-Code-Low-Code AI；工具标签含 Claude Code、Codex、LangGraph、Cursor、LangChain；搜索控件含工作类型、经验、工具、学历、薪资展示；每条跳转到雇主 ATS（Greenhouse/Ashby/Phenom/Zoho）。价格未公示。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| AI Dev Jobs (aidevboard.com) | 「面向 AI 工程岗位的专门市场」，聚合雇主招聘板，含 LLM/agent/infra/研究类技术岗 | AI 开发者、AI 工程技术人员；招聘方 | yes | yes | unknown（求职者免费） | https://aidevboard.com | [官方] 自述 9,384 个岗位、551 家公司、平均薪酬 $234k；暴露 57 个 stack 中的子集（LLM、Agents、RAG、MLOps、Fine-Tuning、PyTorch、NLP Stack 等），并有 AI Agents 角色分类与 `ai-agents` 路径；提供 HTTP MCP 端点与 REST API（13 个工具），`list_tags` / `match_jobs(skills)` 可用于技能筛选；**MCP 是平台集成的协议而非可搜索标签，LangChain 未作为全局筛选项出现**。雇主价目页存在但本次未抓取。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| LLMHire (llmhire.com) | 「AI 劳动力市场情报平台」，聚合实时岗位、薪酬基准与招聘趋势 | LLM/agent 方向 AI 工程师；招聘 AI 原生技术人才的企业 | yes | partial | free（求职者）/ 雇主「Post your role for free」与「Post a Job — From $99」并存 | https://llmhire.com/blog/ai-agent-engineer-most-wanted-role-april-2026 | [官方] 自述聚合 170+ 家公司（Greenhouse/Lever/Ashby/直发），每 4 小时更新；基于 1,247 条 agent 工程岗位给出技能需求分布：Claude/Anthropic SDK 73%、多步 prompt 编排 68%、tool use/function calling 含 MCP 65%、评测设计含 LLM-as-judge 61%、MCP 54%、LangGraph 49%、RAG 44%、可观测性 39%、A2A/多智能体 27%/24%。但**站内实际筛选项与标签体系未在页面中说明**，技能维度以报告形式呈现。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| AIJobs.ai (aijobs.ai) | AI-only 招聘板（AI/ML 岗位） | AI/ML 岗位求职者；招 AI 人才的企业 | yes | partial | $299/条/30 天；3 条包 $749；5 条包 $1,099；10 条包 $1,799；置顶加购 $49；求职者免费 | https://theairegistry.com/tools/aijobsai | [第三方] 价格与套餐来自多个第三方评测（https://www.challengingvoice.com/?p=7424/）；[官方] 存在机器学习分类（第三方审计记为 551 条 ML 岗位，https://theairankings.com/ai-jobs/machine-learning-jobs）。**是否有 AI Agent / LangChain / MCP 级技能标签未能从公开资料确认，需实操验证**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Foorilla（原 ai-jobs.net） | 通用开发者招聘平台，设 Data / AI & Machine Learning 专区 | 技术岗位求职者；中小团队招单个 AI 岗 | partial | partial | 精选位 30 天 $192 / 60 天 $256 | https://jobsitedir.com/jobboard/foorilla.com | [第三方] 定价来自第三方目录站（该站同时注明站内未见公开价）；**该站已非 AI 专属**，AI 岗与 DevOps/Help Desk/通用技术岗并列。历史审计记载 ai-jobs.net 已「消失并跳转至 foorilla」（https://theairankings.com/ai-jobs/machine-learning-jobs，核验日 2026-09-22）。旧站曾提供 LLM/RAG 等技能过滤页（如 /jobs/skill-vision-language/）。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| 80,000 Hours Job Board (80000hours.org) | 面向全球重大议题（含 AI 安全 / 转型性 AI TAI）岗位的策展招聘板 | AI 安全、AI 治理、EA/EB 领域从业者 | partial | partial | unknown | https://80000hours.org/ | [第三方] 自述 900+ 在招岗位；2026 年 7 月公开声明「加大 AI 聚焦」，不再发布 TAI/AI 安全之外的中高级岗位；分类含 Technical AI Safety Research、AI Governance & Policy、AI Security、AI Hardware 等。**偏 AI 安全方向，非通用 Agent 工程**，Agent 工程岗位覆盖度需实操验证。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| AgentJobs.com（同名占位站） | 「面向自主软件劳动力的即将上线的招聘板」，连接雇主与「工程师、研究者与构建者」 | AI agent / 自主软件方向工程师、研究者、构建者 | unknown | unknown | unknown | https://agentjobs.com | [官方] **仅「Launching soon」占位页，无岗位、无筛选、无定价**，未定义 agentic AI 概念。**与本项目名称/域名高度冲突**，需尽快确认品牌与域名可用性（另 agentjobs.io 为 GoDaddy 停放域名，https://agentjobs.io）。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| JobForAgent.com | 「第 1 个面向自主 AI agent 的招聘板」——**招聘对象是 AI Agent 本身，不是开发 agent 的工程师** | 希望用 agent 承接任务的公司；agent 构建者 | no（不服务 agent 开发者求职） | unknown | unknown | http://jobforagent.com/presskit | [第三方] 由波兰的 Kamil Stanuch 与 Łukasz Wróbel 于 2024 年 12 月创办，自述 300+ 构建者，岗位人工核验，另有「AI Job Analyzer」对职位 URL 打分（已分析 237+ 岗位，平均约 41%）。**注意与 AgentJobs 定位区分：这是「给 agent 找工作」而非「给 agent 开发者找工作」**。直接抓取 presskit 未返回内容，数据全部来自[第三方]报道。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| DigitalJobs.com | 号称「全球首个同时面向人类与 AI agent 的职位平台」 | 需要 AI agent 承接数字工作的企业；agent 构建者 | no（不服务 agent 开发者求职） | unknown | unknown | https://www.jobboardhive.com/?p=2375 | [第三方] 2026 年 9 月宣布上线，自述 120,000+ 岗位、6,000+ 公司，联合创始人「Jobsworth」本身是过滤幽灵岗位、支持语音搜索的 AI agent。**属相邻赛道（agent 求职而非 agent 开发者求职），对 AgentJobs 的启示是「双轨人群」设计而非直接竞品**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| No Code Jobs (nocodejobs.org) | 主打 agent 友好（机器可读）的岗位发布板 | 招聘低代码/无代码方向的雇主与 agent 构建者 | no（不服务 agent 开发者求职） | unknown | 免费（雇主） | https://www.bestaifor.com/directory/no-code-jobs | [第三方] 2026-05-29 上线，约 10 条在招，提供 agent 可读的 jobs.json feed 与 MCP 集成；合同/项目岗标注预算 $750–$2,500。**相邻赛道**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Humanless (gohumanless.ai) | 自称「AI Agent 的 Indeed」 | 采购 AI agent 劳动的企业 | no（不服务 agent 开发者求职） | unknown | unknown | https://www.jobboardhive.com/?p=2375 | [第三方] 仅见名称与一句话定位，**无任何可核实的岗位量、筛选或定价资料，需实操验证**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| AI Jobs UK (artificialintelligencejobs.co.uk) | 英国 AI 岗位招聘板 | 英国 AI 岗位求职者；英国雇主 | partial | unknown | £99 起 / 30 天 | https://artificialintelligencejobs.co.uk/hire/pricing | [第三方] 定价来自该站 hire/pricing 页被检索摘要引用。技能标签体系未见公开资料。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Jobs in AI (jobsinai.com) | 定价透明的 AI 岗位发布板 | AI 岗位求职者；招 AI 人才的企业 | partial | unknown | $300/月 基础岗位发布（加购：Newsletter Booster $59、Social Amplifier $30、Cross-Post $100） | https://www.jobsinai.com/pricing | [官方] 存在独立 pricing 页并被第三方索引引用；**具体筛选/标签粒度未公开，需实操验证**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |

### 2.2 第二类：通用招聘平台对 AI/ML/Agent 岗位的支持

| platform | positioning | target_users | agent_job_availability | skill_tag_support | pricing | source_url | notes |
|---|---|---|---|---|---|---|---|
| LinkedIn | 全球最大职业社交与招聘网络 | 各行业求职者与招聘方 | partial | partial | unknown（无固定单价，CPC 竞价） | https://www.linkedin.com/help/recruiter/answer/a6513108 | [官方] LinkedIn 官方帮助页确认 Recruiter 侧有 **AI-Assisted Search（自然语言检索，编译为分面+关键词）** 与技能筛选；[第三方] 归纳指出岗位的 `skills` 数组仅约 50% 岗位被填充，画像 Skills 区可置顶 3 项技能。**未检索到任何官方的「AI Agent」岗位筛选器或技能标签**；官方唯一自称 agent 的产品是招聘方侧的 **LinkedIn Hiring Assistant**（2025-09-03 发布），不是岗位分类。另有[索引]称 LinkedIn 计划 2026 年 9 月起下线经典职位搜索转向 AI 搜索（https://www.applyzee.com/2026/01/Best-Job-Search-Worldwide.html）。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Indeed | 全球最大通用招聘搜索引擎 | 通用求职者与雇主 | partial | partial | unknown（CPC 竞价，无固定单价） | https://www.indeed.com/help/job-seekers/articles/204488950 | [官方] Indeed 帮助页列出实际筛选项：薪资、工作设置、**工作领域（industry or field，唯一的类目型分面）**、职位类型、学历、发布日期，以及 `title:` `company:` 等高级语法。官方明确**没有独立「AI」筛选器**，AI 岗只能靠关键词命中。雇主侧 Indeed Smart Sourcing 有 AI 职位名称分类（AI Architect / AI Developer / AI/ML Engineer / Machine Learning Engineer 等）。[第三方] 2026-02-10 上线 ChatGPT App（@Indeed），与 profile 匹配，不改变站内分类结构。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Glassdoor | 职位 + 薪资估算 + 面试评价的招聘平台 | 注重研究公司口碑与薪资的求职者 | partial | no | unknown | https://hrtechfeed.com/glassdoor-launches-ai-driven-glassdoor-recruiter-to-end-job-search-burnout-and-mass-applications | [第三方] 未检索到 Glassdoor 官方「AI jobs」专区或 AI 专属筛选面；2026 年 10 月推出 AI 驱动的 **Glassdoor Recruiter**（按技能、薪酬、福祉、文化逐次推荐单个岗位）。**属招聘方侧 AI，非岗位标签体系**。注意 Glassdoor 与 Indeed 同属 Indeed 集团。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| ZipRecruiter | 面向中小雇主与求职者的通用招聘平台 | 通用求职者；中小雇主 | partial | partial | unknown | https://www.joveo.com/blog/job-search-inside-chatgpt | [第三方] 筛选维度为职位类型、距离、发布日期、薪资、远程、雇佣类型；2026-03-19 上线 ChatGPT App（@ziprecruiter）。Indeed 官方帮助页称在 AI 搜索（如 ChatGPT）中排名靠前的岗位（如赞助岗位）更容易被呈现，雇主无法选择退出，也无单独的 AI 引荐统计。**未检索到 AI Agent 专属专区或技能标签**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| BOSS直聘 (zhipin.com) | 中国直接招聘平台 | 中国求职者与企业 | partial | unknown | unknown（企业端定价未公开核实） | https://www.zhipin.com/job_detail/97ac8240ab1c2a2703R_0ty5FVFX.html | [第三方] 站内已有「AI Agent 产品经理」「大模型算法工程师/专家（agent 算法）」「AI 模型-Agent 技术（华为校招）」等具体岗位，说明 Agent 岗位**存在但无独立专区**；[第三方] 2026-09 深圳开放日称 AI 岗位分工细分为「调机器/用机器干活/校机器」，超 150 万求职者使用 BOSS 直聘 AI 服务。**技能标签筛选粒度与是否有 Agent 标签需实操验证**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| 脉脉 (Maimai) | 中国新经济职场社交与招聘平台 | 中国 AI/新经济从业者与企业 | partial | unknown | unknown | https://www.workercn.cn/c/2026-09-17/8895694.shtml | [第三方] 2026 年 9 月发布《Agent 重置职场——AI 人才流动报告》：2026 年 1–7 月新发 AI 岗位同比 +789.47%，新发 AI 岗位平均月薪 ¥63,160；岗位结构 AI 应用开发 60.97% / 技术底座 24.55% / 业务效能 14.48%；**「Agent 开发工程师」为企业最热招岗位**；FDE/现场部署工程师扩招 +1,522.73%。**脉脉是报告发布方而非 agent 岗位招聘板**，无 Agent 专区。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |

### 2.3 第三类：技术招聘平台对 AI 岗位的覆盖

| platform | positioning | target_users | agent_job_availability | skill_tag_support | pricing | source_url | notes |
|---|---|---|---|---|---|---|---|
| Wellfound (原 AngelList Talent) | 面向初创公司的远程招聘市场，候选人自荐 + 招聘方直连 | 初创公司创始人与早期团队；中高级技术人才 | partial | partial | Job Ads 起价 $200；Reach AI 招聘代理 $0/$135/$199 每席/月；Recruit Pro $499/月；Autopilot $500/月每岗 + 10% 安置费 | https://www.cloudspress.com/angellist-explained-venture-infrastructure-startup-tools-and-what-happened-to-angellist-jobs | [第三方] 自述 130,000+ 岗位、27,000+ 初创公司；支持角色、远程、薪资、股权、融资阶段筛选。审计实测（2026-09-22）远程 ML Engineer 302 条、远程 AI Engineer 6,701 条，**数量以宽泛标题口径计，未见 agent 专属标签**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| YC Work at a Startup | YC 公司专属招聘入口 | YC 生态公司的前 10 号员工招聘 | partial | partial | unknown（未见收费） | https://theairankings.com/ai-jobs/machine-learning-jobs | [第三方] 审计记载「未公开，列表需登录个人档案后才可见」；被 RoamJobs 2026 评为初创岗位第 2。**无任何技能标签体系**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Welcome to the Jungle（含 Otta） | 欧洲（法/荷/英）策展型科技招聘板，强薪资与公司文化信息 | 欧洲技术/产品/设计人才；欧洲雇主 | partial | partial | unknown | https://apify.com/glasswing/welcome-to-the-jungle-jobs/api/openapi | [第三方] Otta 于 2024-01-22 被 Welcome to the Jungle 收购；可按关键词、城市、国家、合同类型、`remoteOnly` 筛选，**未发现 AI/Agent 专属筛选面**；AI/ML 岗位混在 Software Engineering / Data 等类目下。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Remote OK (remoteok.com) | 免费、仅远程、标签驱动的岗位板 + 公开 JSON API | 远程技术从业者；希望触达远程人才的公司 | partial | partial | $299–$599/条（[第三方] 口径） | https://apify.com/slate_cyclone/remoteok-jobs-scraper | [第三方] 官方分类仅 exec/medical/finance/education/ops/marketing/design/dev，**没有官方「remote AI jobs」类目**（https://www.remoteok.com/remote-ai-jobs 抓取返回 302 回首页）；AI 相关靠雇主自设标签（python/llm/machine-learning/ai/gpt/ml 等，每岗 3–8 个），被第三方称为「质量最高的分类信号」；公开 API 支持 `?tag=` 查询。**是否有 agent 级标签需实操验证**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| We Work Remotely (weworkremotely.com) | 仅远程岗位板，2007 年起，付费发布过滤低质雇主 | 远程技术/设计/产品人才 | partial | no | $299/条/30 天（一次性），多岗位套餐最高 40% 折扣，另有可见度加购档；求职者免费 | https://www.remogrid.com/blog/reviews/we-work-remotely-review-2026-job-board-quality | [第三方] $299 定价与套餐被多方引用；[第三方] 多个来源一致指出**没有独立 AI/ML 分类**，AI 岗混在 Programming 类目，搜索本身「基础，无技能栈筛选」。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Hacker News「Who is hiring」 | 每月 HN 社区自发互贴帖（雇主侧 / 求职者侧） | 愿意用论坛帖投递的技术候选人 | partial | no | 免费（无平台费用） | https://news.ycombinator.com/item?id=50004401 | [官方] 2026-10 月雇主帖 id=50004401 含「构建拟人化 AI 语音/面貌 agent」的岗位；2026-06 月 id=48364864 含 Factory AI 的 AI Engineer (agentic systems, LLM integrations, evals)。**纯文本帖子，无筛选、无标签、无结构化岗位字段**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Built In | 面向美国企业雇主的公司+岗位聚合板，内联显示薪资带 | 美国中高端技术求职者；美国企业 | partial | no | unknown | https://theairankings.com/ai-jobs/machine-learning-jobs | [第三方] 审计实测 ML 分类 50 页、ML Engineer 73 页（2026-09-22）；ML 岗散落在 ML Engineer / AI Engineer / Applied Scientist / MLOps 等标题族中，**无 AI Agent 专属分类**，且不含前沿实验室岗位。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Stack Overflow Jobs (stackoverflow.jobs) | 面向开发者社区的技术岗位板（原属 Stack Overflow） | 开发者工程师 | unknown | partial | unknown | https://theairankings.com/ai-jobs/machine-learning-jobs | **状态存疑**：[第三方] 有来源称其与 Hired、Triplebyte/Karat、Kaggle Jobs、Papers With Code 一并已关停；但本次 `curl` 直连返回 **HTTP 403**（存在但拒绝抓取），另有[第三方]（https://uxcel.com/blog/top-ai-job-boards）仍将其列为活跃并称支持 machine-learning / AI / NLP / PyTorch 标签。**结论：不能断言已关停也不能断言活跃，必须实操打开站点确认**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Levels.fyi Jobs | 薪酬透明的技术岗位库，绑定公司薪酬数据 | 高薪技术候选人；高阶工程岗位 | partial | no | unknown | https://theairankings.com/ai-jobs/machine-learning-jobs | [第三方] 审计确认为活跃；数据（2026-08-15）ML Engineer 总薪酬中位 $278,000，AI Engineer $159,430。**以薪资数据为核心，非岗位发现工具，无技能标签**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Arc.dev | 远程优先的开发者自由职业市场 + 招聘方市场 | 高质量远程工程师；需要外包/驻场 AI 能力的公司 | partial | partial | 企业端合同访问免费；工程师费率常见 $50–$150/小时（多见于中高级） | https://arc.dev/employer-blog/contra-alternatives/ | [第三方] 自述约 450,000 名工程师、主张「top 2%」，用 HireAI 做匹配；[第三方] 指其 AI 岗覆盖弱（对比表列 AI Engineer 与 Data Engineer 岗位数为空）。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Braintrust | 非营利技术人才网络，技能画像 + 技能匹配招聘 | AI/ML 方向自由职业工程师；美国企业客户 | partial | yes | 自由职业者保留 100% 费率；客户支付平台固定费（约 10–15% 或客户会员费） | https://www.secondtalent.com/resources/7-best-freelance-platforms-ai-developers | [第三方] 以**已验证技能**为核心的结构化画像，**技能导向的匹配**是其主要卖点，被评为适合 agentic AI 招聘工作流；资深美国 AI 工程师常报 $100+/小时。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Toptal | 高端筛选式技术人才网络（宣称通过率约 3%） | 寻求高阶外包/合同技术人才的企业 | partial | partial | 公开费率区间：开发者 $60–$80/小时，资深/专长 $100–$200+（平台有隐性加价） | https://cadence.withremote.ai/blog/arc-vs-toptal | [第三方] 匹配约 48 小时，支持最长两周试用；**费率由平台与人才协商、无公开价目卡**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Contra | 零佣金自由职业平台，以作品集+客户评价审核 | 独立开发者；小型团队 | partial | no | 合同 0% 平台抽成；典型费率 $30–$150/小时 | https://arc.dev/employer-blog/contra-alternatives/ | [第三方] 对比中**明确指出 Contra 在 AI 原生岗位寻访与审核深度上较弱**。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |
| Honeypot (honeypot.io) | 德语区/荷兰语区的开发者反向市场（开发者一个档案，企业带薪资来申请） | 荷兰、德国的高阶开发者；德荷雇主 | partial | partial | 雇主按年薪收取约 15% 成功费；求职免费 | https://www.webfolio.to/tools/ai-jobsnet | [第三方] 被多方列为德荷区首选科技板；**未检索到 AI/Agent 专属专区或 AI 技能标签**，AI 岗混在科技岗中。satisfaction_score 留空，需 H3.1/H3.2 实操填写 |

---

## 3. 分类归纳

### 3.1 第一类：AI / Agent 垂直招聘平台 —— **存在，且不止一家**

**关键发现**

1. **「专门面向 AI Agent 开发者的求职平台」这个形态在 2026 年已经存在，且至少有 5 个独立运营的实例。**
   - 明确以 agent 为唯一主题的：**agenticengineeringjobs.com**（AXIA Enterprises，200 个在招 agentic 岗位）、**agentic-engineering-jobs.com**（Maxim Buz / Heazy Studio，500+ 在招）、**agenticcareers.co**（2,962 岗位 / 890 公司）、**ai-native-builder.com/ai-agent-jobs**（300 个在招）、**aidevboard.com**（9,384 岗位 / 551 公司，57 个 stack）。
   - **这直接削弱了 AgentJobs「市场上不存在专门面向 AI Agent 开发者的求职服务」这一前提假设。**（来源：各站官方页面，见 §2.1）
2. **赛道内部已经分化出三种定位**：
   - **岗位分类法型**（agenticengineeringjobs.com 的 7 类角色 + 薪资带）→ 以「角色」而非「技能」为轴；
   - **框架/技能标签型**（agentic-engineering-jobs.com 按 LangGraph/CrewAI/Pydantic AI/RAG/multi-agent/observability/evals 筛；ai-native-builder 按 Claude Code/Codex/LangGraph/Cursor/LangChain 打标签；aidevboard 的 57 stacks 含 Agents/RAG/Fine-Tuning）→ 以「栈」为轴；
   - **数据/情报型**（agenticcareers.co 的 CC BY 4.0 开放数据集；llmhire.com 的技能需求分布报告）→ 以「市场数据」为轴。
   **AgentJobs 需要明确自己落在哪一轴上，否则会被当作「又一个 agent 岗位板」。**
3. **技能标签的存在性已获证实，但口径不统一。** 已公开的 Agent 相关标签集合至少包括：LangChain、LangGraph、LlamaIndex、CrewAI、AutoGen、MCP、RAG、Anthropic/Claude SDK、tool use/function calling、multi-agent、A2A、agentic coding、Claude Code、Codex、Cursor、evals、observability、LangSmith、Pydantic AI。**没有任何一家平台公开了「完整统一」的 agent 技能本体（ontology）**——不同平台的标签集合互不兼容，这本身是机会点。
4. **「Agent 开发工程师」已被官方确认为独立岗位类别。** 脉脉《Agent 重置职场》报告（2026-09）显示该职位为 2026 年 1–7 月企业最热招 AI 岗位，新发 AI 岗位同比 +789.47%，AI 应用开发占 60.97%。
5. **出现了一个必须警惕的同名产品**：**agentjobs.com** 已存在，为「面向自主软件劳动力的即将上线招聘板」。同时 `agentjobs.io` 为停放域名。这是 AgentJobs 的品牌与域名风险（需实操核查其主体与开发进度）。
6. **必须区分「给 agent 找工作」与「给 agent 开发者找工作」两类产品。** JobForAgent.com、DigitalJobs.com、No Code Jobs、Humanless 属于前者（agent 作为求职者）。它们与 AgentJobs 的开发者求职主赛道**不构成直接竞争，但共享「AgentJobs」品牌语义，是品牌混淆与 SEO 冲突来源。**

### 3.2 第二类：通用招聘平台 —— **有海量 AI 岗位，但没有任何 Agent 专属结构**

**关键发现**

1. **四大通用平台（LinkedIn / Indeed / Glassdoor / ZipRecruiter）均未提供「AI Agent」岗位专区或 AI Agent 技能标签。** Indeed 官方帮助页明确其唯一类目型分面是「工作领域（industry or field）」，AI 岗只能靠关键词命中；We Work Remotely、Glassdoor 同类。
2. **通用平台的 AI 能力全部投在「招聘方侧」而非「岗位结构侧」**：LinkedIn Hiring Assistant（2025-09，LinkedIn 唯一自称 AI agent 的产品）、Indeed Talent Scout / Smart Sourcing、Glassdoor Recruiter（2026-10）。**这些产品改变的是匹配与筛选体验，不改变岗位分类维度。**
3. **技能标签是通用平台的已知弱点**：LinkedIn 岗位的 `skills` 数组仅约 50% 被填充，其余需关键词兜底（第三方观测）；LinkedIn 也无面向用户的「AI Agent」技能筛选器。
4. **2026 年的新变量是「AI 助手即搜索入口」**：Indeed（2026-02-10）与 ZipRecruiter（2026-03-19）先后上线 ChatGPT App，Upwork 于 2026-04-09 跟进。Indeed 官方称在 AI 搜索中排名靠前的岗位更容易被呈现，且**雇主无法选择退出、无独立 AI 引荐统计**。
   → **对 AgentJobs 的直接含义：AI 入口正在把「结构化岗位数据」从加分项变成分发前提。岗位数据若要进入 ChatGPT/Claude 等助手的答案，必须是规范化的标题、薪资、地点与远程状态。**
5. **中国市场同构**：BOSS 直聘站内已有大量「AI Agent 产品经理」「agent 算法」岗位但无独立专区；脉脉以《Agent 重置职场》报告的形式确认了 Agent 开发工程师岗位的独立性与爆发式增长（+789.47% YoY）。

### 3.3 第三类：技术招聘平台 —— **覆盖 AI，但标签体系弱、Agent 专门化低**

**关键发现**

1. **技术板普遍不做技能栈筛选。** We Work Remotely 被[第三方]明确评价为「基础搜索，无技能栈筛选」；Built In 的 ML 岗散落在标题族中；Stack Overflow Jobs 虽被称有 machine-learning/AI/NLP/PyTorch 标签，但**其平台是否仍在运营存在直接冲突的来源（一方称已关停，一方称活跃；本次 curl 返回 403）**。
2. **唯一把「标签」当核心的通用技术板是 Remote OK**，但它没有官方 AI 类目，AI 相关靠雇主自设标签（python / llm / machine-learning / ai / gpt / ml 等），且 `/remote-ai-jobs` 路径 302 回首页。**技术板把「技能」当作描述性元数据，而 Agent 垂直板把「技能」当作筛选轴——这正是 AgentJobs 差异化的立足点。**
3. **薪资透明是技术板已被验证的付费理由**：WWR $299/条、Wellfound Job Ads 起价 $200、Levels.fyi 以薪酬数据为核心、Otta/WtJ 强推薪资与股权透明。**AgentJobs 若以「Agent 技能可验证」为卖点，需回答「为什么值得付费」——可参照「薪资透明」这一已被市场接受的价值锚。**
4. **自由职业/外包侧同样有 agent 岗位供给**，Braintrust 明确以「已验证技能」画像做匹配并被点名为适合 agentic AI 寻访，但**平台池子小于 Upwork、周期更长**；Arc.dev 自称 45 万工程师但 AI 岗覆盖被对比表标注为空白；Contra 被明确评价 AI 原生寻访能力弱。
5. **重要存量事实**：Kaggle Jobs（2020-12-22 弃用）、Papers With Code（据第三方报道 2025-07-24 停止服务）、Triplebyte（2023-03-31 关停）、Hired（约 2024-05 关停）、Otta（2024-01-22 被 WtJ 收购）、ai-jobs.net（已跳转 Foorilla）均已退出或转型。**垂直 AI 招聘板的历史死亡率很高，这对 AgentJobs 的商业模式设计是一个硬约束信号。**

---

## 4. 需实操验证清单（移交 tasks.md 任务 6 [H3.1] / 任务 7 [H3.2]）

> 以下每一项**无法通过公开资料获得**，必须由创始人真人打开平台完成，并留存截图作为 `evidence_url`。优先级 P0 = 影响产品定位判断，P1 = 影响竞品表完整性，P2 = 影响商业化设计。

### 4.1 优先级 P0 —— 影响 AgentJobs 差异化是否成立

| # | 平台 | 要验证什么 | 验收标准 |
|---|---|---|---|
| V1 | **agenticengineeringjobs.com** | ①「200 个在招 agentic 岗位」是否属实、可点开多少条；②岗位是否真跳转到雇主 ATS；③是否有可用的技能标签筛选（实测找 LangChain / MCP / LangGraph）；④岗位发布时间分布与重复率 | 至少 20 条岗位的抽样统计 + 3 张截图 |
| V2 | **agentic-engineering-jobs.com** | ①**定价到底是免费还是 $150/条**（本次 `/about` 与 `/employers` 检索结果直接冲突，`/employers` 抓取 404）；②「500+ 在招」的真实性；③ agentic-stack 筛选是否真的可点且能筛出结果 | 定价页截图 + 筛选交互截图 |
| V3 | **agenticcareers.co** | ①2,962 岗位 / 890 家公司口径是否可复现；②公司阶段与栈筛选是否真的存在；③岗位是否点回原始 ATS；④是否有隐藏收费 | 首页 + 筛选截图 |
| V4 | **ai-native-builder.com/ai-agent-jobs** | ①300 个在招是否属实（页面标注 2026-10-24 更新）；②工具标签（Claude Code / Codex / LangGraph / Cursor / LangChain）是否可点筛选；③是否有 AI Agent 岗位专区入口 | 标签筛选截图 + 至少 30 条岗位抽样 |
| V5 | **aidevboard.com** | ①57 个 stack 中是否有 MCP / LangChain 级标签；②9,384 岗位 / 551 公司的真实性；③MCP API 是否真的返回带 agent 标签的岗位；④**AI Dev Jobs MCP 的 `match_jobs(skills)` 与 `list_tags` 实际返回的标签清单** | 直接调用 `/mcp` 与 REST API 并记录返回的完整标签列表 |
| V6 | **llmhire.com** | ①站内实际筛选轴（是否能把 Claude Agent SDK / MCP / LangGraph 当筛选项）；②技能需求分布数据是站内筛选还是仅报告文案 | 站内搜索截图 |
| V7 | **LinkedIn** | ①是否存在任何面向用户的「AI Agent」技能筛选；②岗位 `skills` 填充率实测（抽 30 条 agent 岗）；③AI-Assisted Search 对 agent 岗位的实际召回质量 | 30 条岗位抽样 + 搜索截图 |
| V8 | **Indeed / Glassdoor / ZipRecruiter** | ①是否有隐藏的 AI/AI Agent 类目入口（需登录后翻找分类页）；②关键词搜 "AI Agent" 的岗位噪声比 | 各 1 次登录态检索截图 |

### 4.2 优先级 P1 —— 补全竞品对比表

| # | 平台 | 要验证什么 |
|---|---|---|
| V9 | **agentjobs.com**（同名占位站） | 主体是谁、是否即将上线、定位是否与 AgentJobs 完全重叠——**这是品牌/域名冲突评估，最高商业优先级** |
| V10 | **Stack Overflow Jobs** | **直接打开 https://stackoverflow.jobs 确认是否仍运营**；若运营，实测 machine-learning / AI / NLP / PyTorch 标签是否真实可用 |
| V11 | **Remote OK** | 实测 `/remote-ai-jobs` 或 `?tag=llm` / `?tag=machine-learning` 的实际岗位量与去重后数量；是否存在 agent 级标签 |
| V12 | **We Work Remotely** | 站内是否真的无 AI/ML 分类（本次仅得第三方口径）；搜 "AI agent" 的结果数 |
| V13 | **Wellfound** | 实测是否存在 AI Agent 标签；抽 20 条 agent 岗看技能要求；实测远程 AI Engineer 岗位数（审计口径 6,701 需复现） |
| V14 | **BOSS 直聘 / 脉脉** | 站内是否有 AI Agent 岗位专区/筛选标签（本次仅确认岗位存在，无专区证据） |
| V15 | **AIJobs.ai / Foorilla / Jobs in AI / AI Jobs UK** | 逐一确认公开定价是否与本次记录的第三方口径一致；是否有 agent 级技能标签 |
| V16 | **80,000 Hours** | Agent 工程岗位（非 AI 安全）的实际覆盖量 |
| V17 | **Hacker News Who is hiring** | 2026-10 / 2026-11 月帖中 agent 岗的实际条数与可检索性（本次为人工阅读抽样） |

### 4.3 优先级 P2 —— 商业化与体验

| # | 平台 | 要验证什么 |
|---|---|---|
| V18 | 全部 AI 垂直平台 | 求职者端是否完全免费、投递是否需注册、是否有付费加速/置顶——决定 AgentJobs 收费侧设计 |
| V19 | **Braintrust / Arc.dev / Toptal / Contra** | 实际可搜到的 agent 岗位数与匹配质量，用于判断「人才侧聚合」是否已被满足 |
| V20 | **JobForAgent / DigitalJobs / No Code Jobs / Humanless** | 确认这批「给 agent 找工作」的产品是否真的会向 agent 开发者溢出（品牌混淆是否真实发生） |

### 4.4 需补齐的字段（M10）

| 字段 | 说明 |
|---|---|
| `satisfaction_score` | **本文件全部留空。** M10 为低优指标（通过值 ≤ 5/10），必须由创始人按 H3.1（通用平台）/ H3.2（技术平台）实操打分，附截图。**Agent 负责不得打分。** |

---

## 5. 对 AgentJobs 差异化定位的初步启示

> 以下每条均标注其依据的来源证据。凡标注「需实操」的结论在验证完成前不得写入对外材料。

**1. 「不存在专门面向 AI Agent 开发者的求职平台」这一前提不成立，必须放弃，改写为「已有平台但存在结构性空隙」。**
依据：agenticengineeringjobs.com（200 岗位，官方页）、agentic-engineering-jobs.com（500+ 岗位，官方页）、agenticcareers.co（2,962 岗位，官方页）、ai-native-builder.com（300 岗位，官方页）、aidevboard.com（9,384 岗位，官方页）。**这五条官方来源共同证明赛道已存在且供给不小。**

**2. 真正的空隙是「技能本体不统一 + 岗位数据不可被机器消费」，而不是「没有岗位专区」。**
依据：五家垂直平台的标签集合互不兼容（agenticengineeringjobs.com 用 7 类角色轴、无技能标签；agentic-engineering-jobs.com 用 LangGraph/CrewAI/Pydantic AI 轴；ai-native-builder 用 Claude Code/Codex/Cursor 轴；aidevboard 用 57 stacks 轴；llmhire.com 只发布技能需求分布报告而不做筛选）；而通用侧 Indeed 官方帮助页确认 AI 岗只能靠关键词命中（无类目分面），LinkedIn 岗位 `skills` 数组仅约 50% 填充。**结论：AgentJobs 的定位应落在「统一的 Agent 技能标签本体 + 结构化岗位数据」，而不是「第一个 Agent 岗位板」。**

**3. 「agent 工程」已被官方确认为独立岗位类别，AgentJobs 的品类命名窗口真实存在。**
依据：脉脉《Agent 重置职场》报告（2026-09）明确「Agent 开发工程师」为企业最热招 AI 岗位，新发 AI 岗位同比 +789.47%，AI 应用开发占 60.97%（https://www.workercn.cn/c/2026-09-17/8895694.shtml）；agenticengineeringjobs.com 官方把 AI Agent Engineer 单列为一类角色并给出 $120k–$350k 薪资带；agenticcareers.co 官方统计 AI Agent Engineer 占其岗位的 15.3%。**注意：该品类是「AI 应用开发」大类的子集（60.97%），AgentJobs 不应把自己定位成与整个 AI 岗市场对立的品类。**

**4. 通用平台的 AI 投入全在招聘方侧，这既是威胁也是缺口。**
依据：LinkedIn Hiring Assistant（2025-09-03，官方帮助页 https://www.linkedin.com/help/recruiter/answer/a6513108）、Glassdoor Recruiter（2026-10，https://hrtechfeed.com/...）、Indeed Talent Scout/Smart Sourcing（官方 https://www.indeed.com/candidates）。**这些产品改善的是匹配与排序，不改变岗位分类维度；一旦 AgentJobs 把 agent 岗位结构化并供给给招聘方工具，通用平台会是最快的下游客户而非竞品。**

**5. 「AI 助手即搜索入口」把结构化岗位数据从加分项变成分发前提，应前置到 MVP。**
依据：Indeed 官方说明——在 AI 搜索中排名靠前的岗位更容易被呈现、雇主无法选择退出、无独立 AI 引荐统计（https://www.joveo.com/blog/job-search-inside-chatgpt）；Indeed 与 ZipRecruiter 分别于 2026-02-10、2026-03-19 上线 ChatGPT App，Upwork 于 2026-04-09 跟进。**含义：岗位的标题规范化、显式薪资区间、准确地点/远程状态、以及可被 LLM 直接引用的语义结构，应作为 AgentJobs 的基础数据要求，而不是后期增强。**

**6. 差异化价值锚应向「可验证」靠拢（参照已被市场接受的「薪资透明」），并规避「免费+泛化」陷阱。**
依据：已被验证的付费理由是薪资/股权透明——We Work Remotely $299/条、Wellfound Job Ads 起价 $200、Levels.fyi 以薪酬数据为核心、Otta/WtJ 强推薪资与股权透明、agentic-engineering-jobs.com 转向 $150/条 + $2,990/年包年（[第三方]口径）；而免费板（agentic-engineering-jobs.com 早期、No Code Jobs）供给量极小。**同时，垂直 AI 板的历史死亡率极高**（Kaggle Jobs 2020-12-22 弃用、Papers With Code 2025-07-24 停止服务、Triplebyte 2023-03-31 关停、Hired 约 2024-05 关停、ai-jobs.net 已跳转 Foorilla）**——这要求商业模式不要建立在「免费聚合 + 广告」这一已被验证容易出局的路径上。需实操补充：V18（求职者端收费与投递门槛）。**

**7. 品牌与域名冲突是紧迫事项，优先级高于任何功能设计。**
依据：agentjobs.com 已是「Launching soon」的自主软件劳动力招聘板（官方页 https://agentjobs.com），agentjobs.io 为停放域名（https://agentjobs.io）；JobForAgent.com / DigitalJobs.com / No Code Jobs 占据了「Agent 求职」语义。**建议在验证期同步完成商标与域名检索，并将品牌与「给 agent 找工作」类目显式区隔。**

---

## 6. 证据强度说明

### 6.1 证据充分（官方页面直接抓取核实，可直接引用）

| 结论 | 证据类型 | 来源 |
|---|---|---|
| 5 家 agent 垂直平台的定位、岗位量、筛选维度、薪资带 | 官方页面直接抓取 | agenticengineeringjobs.com/llm-info、agenticengineeringjobs.com 首页、agentic-engineering-jobs.com/about、agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026、agenticcareers.co/state-of-agentic-hiring、agenticcareers.co/blog/how-to-break-into-the-agentic-economy-2026、ai-native-builder.com/ai-agent-jobs、aidevboard.com |
| 垂直板已覆盖的 agent 技能标签清单（LangChain/LangGraph/MCP/RAG/Claude Code/Codex 等） | 官方页面 + 官方市场报告 | 同上；agentic-engineering-jobs.com 的 1,135 条岗位框架分析 |
| Indeed 无独立 AI 筛选器、仅有「工作领域」分面 | 官方帮助页 | indeed.com/help/job-seekers/articles/204488950 |
| LinkedIn Recruiter 的 AI-Assisted Search 与技能筛选存在 | 官方帮助页 | linkedin.com/help/recruiter/answer/a6513108、/answer/a1673877 |
| Glassdoor 无官方 AI jobs 专区；Glassdoor Recruiter 为 AI 驱动产品 | 第三方行业媒体 | hrtechfeed.com |
| Indeed / ZipRecruiter / Upwork 的 ChatGPT App 上线时间 | 第三方（引 Indeed 官方雇主帮助页） | joveo.com/blog/job-search-inside-chatgpt |
| 通用平台技能字段填充率约 50%、无「AI Agent」技能筛选器 | 第三方观测 | thirdwatch.dev、placementos.ai、apify.com |
| 存量招聘板的关停/并购状态 | 第三方审计（自述核验日 2026-09-22） | theairankings.com/ai-jobs/machine-learning-jobs |
| agentjobs.com 为「Launching soon」占位站、agentjobs.io 为停放域名 | 直接抓取 + HTTP 状态核验 | agentjobs.com、agentjobs.io |
| We Work Remotely 雇主定价 $299/条 | 第三方评测（多源一致） | remogrid.com、toolradar.com、mazikbox.com |
| 80,000 Hours 加大 AI 聚焦、不再发 TAI/AI 安全外的中高级岗 | 官方公告经第三方引用 | 80000hours.org、pulseaugur.com |
| 脉脉《Agent 重置职场》数据（+789.47% YoY、Agent 开发工程师为最热招岗） | 第三方媒体转载官方报告 | workercn.cn、jingjiribao.cn、gmw.cn |

### 6.2 证据中等（官方站内或间接，但关键数字来自第三方）

- **pricing 一栏中的绝大多数数字**（AIJobs.ai $299、Foorilla $192/$256、Wellfound $200/$499/$500、AI Jobs UK £99、Jobs in AI $300/月、Remote OK $299–$599、Arc.dev/Toptal/Contra/Braintrust 费率区间）：均来自第三方评测或对比站，**非平台官方价目页直接抓取**，且多数评测站有自有商业动机。
  → **P1 验证项 V15、V18 与 P2 验证项 V19 需复核。**
- **各平台的岗位数量**（agenticcareers 2,962/890、AI Native Builder 300、aidevboard 9,384/551、agenticengineeringjobs 200、agentic-engineering-jobs 500+、Wellfound 6,701 远程 AI Engineer）：均为平台自述或第三方审计在特定日期的计数，**随时间变化且口径不统一**（有的去重地点、有的按标题宽泛匹配）。
- **agentic-engineering-jobs.com 的定价存在直接冲突**：`/about` 官方页面与发布平台均称「100% free」，而检索索引显示 `/employers` 为 $150/条 + $2,990/年。**直接抓取 `/employers` 返回 404，无法裁定。** → V2 列为 P0。
- **Stack Overflow Jobs 的运营状态存在直接冲突**：一方称已关停（含在 Hired/Triplebyte/Kaggle Jobs/Papers With Code 的关停名单内），另一方仍列为活跃并称有 ML/NLP/PyTorch 标签；本次 curl 直连返回 HTTP 403。**两种可能都未被排除。** → V10 列为 P1。

### 6.3 证据较弱（仅第三方报道，需实操甚至放弃）

- **JobForAgent.com、DigitalJobs.com、No Code Jobs、Humanless**：全部信息来自单一第三方汇总报道；JobForAgent 的 presskit 直接抓取未返回内容。**其岗位量、定价、标签体系均属未证实。**
- **Hacker News Who is hiring 的 agent 岗覆盖度**：本次为人工阅读 2026 年 2/4/6/8/10 月贴的抽样，**非全量统计**，且 HN 帖子无法检索。
- **Wellfound 远程 AI Engineer 6,701 条 / ML Engineer 302 条**：来自 2026-09-22 的第三方审计快照，**口径为宽泛标题匹配，不能等同于「agent 岗」**。
- **Stack Overflow Jobs 的标签体系（machine-learning/AI/NLP/PyTorch）**：仅有第三方综述提及，未直接抓取平台页面。
- **Honeypot 的 AI 岗覆盖**：本次未检索到其站内 AI/ML 分类页，只有间接的第三方评价。
- **脉脉「无 Agent 专区」的判断**：为**未检索到**专区页面，而非证实不存在；BOSS 直聘同理。二者需实操登录态核实（V14）。
- **各类招聘代理/外包机构的 agent 岗供给**（MOR Software、SlashDev、HireDeveloper、Developer Bazaar）：多为 SEO 内容营销页，费率区间不作为定价证据采信，仅作背景。

### 6.4 完全没有证据（明确留空）

| 字段 | 涉及平台 | 原因 |
|---|---|---|
| `satisfaction_score` | **全部 36 行** | M10 属真人实操指标（任务 6/7），Agent 不得打分。**本文件全部留空** |
| `pricing` = unknown | agenticengineeringjobs.com、agenticcareers.co、aidevboard.com 雇主价、llmhire.com 求职者价、AIJobs.dev 类目、LinkedIn、Indeed、Glassdoor、ZipRecruiter、BOSS 直聘、脉脉、Wellfound 求职者价、YC Work at a Startup、Welcome to the Jungle、Built In、Stack Overflow Jobs、Levels.fyi、Arc.dev、Toptal、Contra、Honeypot 求职者价 | 公开资料中未见可引用的价格数字；部分平台本就没有对求职者收费（但未获官方确认） |
| `skill_tag_support` = unknown / no | Indeed 求职者端、Glassdoor、ZipRecruiter、BOSS 直聘、脉脉、Welcome to the Jungle、Hacker News、Built In、Levels.fyi、Contra、AI Jobs UK、Jobs in AI、JobForAgent、DigitalJobs、No Code Jobs、Humanless | 无官方标签清单可引；`no` 仅在有「明确无技能筛选」的第三方评价时使用（WWR、Hacker News、Built In） |

---

## 7. 移交说明（给任务 19 [A3.2]）

1. 本文件 §2 的三张表已结构化为 **`competitors-prefill.csv`**（36 行，5 列已填），任务 19 在其上补两列即可，无需重复录入。
2. `agent_job_availability` 与 `skill_tag_support` 使用受控值 `yes / partial / no / unknown`，与任务 19 的口径一致。预填表中在受控值后附了粒度说明（括号内），便于实操时对照核实。
3. **`satisfaction_score` 列本文件不产出**，须等待任务 6 [H3.1] 与任务 7 [H3.2] 的真人实操记录。
4. `differentiation` 列由任务 19 依据本文件 `notes` 与实操截图统一措辞后填写，**必须使用受控词表**，否则 D1 去重计数失效（`compute_metrics.py` 按字符串精确去重）。
   > **受控词表已随 D1 基准变更而更新（2026-10-31）**：差异化点的参照物改为**垂直竞品**（见 `validation-metrics.md` D1 条目与 `schemas/competitors.md`「D1 计点规则」）。因此本文件原建议的受控词中，**`Agent 岗位专区`、`Agent 技能标签筛选`、`Agent 角色分类法`、`框架标签（LangChain/LangGraph 等）` 四项不再计入 D1**——五家垂直竞品已提供且粒度不逊（agentic 专属岗位分面、7 类角色分类法、LangGraph/CrewAI/Pydantic AI 栈筛选、Claude Code/Codex/Cursor 工具标签）。继续按旧参照系计点会得出「差异化已成立」的错误结论。
   >
   > 修正后的受控词表建议（全部须在垂直竞品基准下成立）：`统一 Agent 技能标签本体`、`岗位数据可被机器消费（MCP/REST/JSON 导出）`、`跨平台技能标签归一`、`岗位语义结构（可被 LLM 直接引用）`、`显式薪资区间`、`agent 岗位专用检索接口`、`面向 agent 开发者的双向评价与作品集`、`按 agent 技术栈深度分类而非仅按角色`。
5. 本文件标记为 **P0 的验证项（V1–V8）建议在任务 19 之前完成**，因为它们直接决定「差异化是否成立」的结论是否需要改写。
6. §5 第 2 条给出的定位（「技能本体不统一 + 岗位数据不可被机器消费」）与新的 D1 基准方向一致，可直接作为受控词表的前两项来源。

---

## 8. 预填表说明（`competitors-prefill.csv`）

| 列 | 状态 | 来源 |
|---|---|---|
| `platform` | ✅ 已填 | 本文件 §2 三表的平台名，逐字对齐 |
| `job_types_covered` | ✅ 已填 | 本文件 `positioning` + `target_users` + `notes` 中的岗位分类信息 |
| `agent_job_availability` | ✅ 已填 | 本文件 `agent_job_availability`（yes/partial/no/unknown）+ 规模自述 |
| `skill_tag_support` | ✅ 已填 | 本文件 `skill_tag_support` + `notes` 中的标签粒度描述 |
| `evidence_url` | ✅ 已填 | 本文件 `source_url` |
| `differentiation` | ⬜ 留空 | D1 计点须逐条给出垂直竞品基准证据（见 §7 第 4 条） |
| `satisfaction_score` | ⬜ 留空 | M10 属真人实操指标（见 §6.4） |

```bash
cp validation/schemas/competitors-prefill.csv validation/data/competitors.csv
python3 validation/compute_metrics.py --data-dir validation/data
```

> 该预填表已通过 `compute_metrics.py` 的真实 schema 校验（36 行、7 列、表头与 schema 逐字一致）。此前 `satisfaction_score` 被声明为必填，会使「公开资料已填、满意度待实操」这一必然的中间状态直接触发 schema 错误（退出码 2），打分表根本跑不出来；该列已改为可空，M10 按已打分平台的均值计算。
