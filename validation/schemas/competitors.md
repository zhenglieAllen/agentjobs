# competitors.csv —— 竞品结构化对比表

**权威来源**：任务 6 [H3.1] + 任务 7 [H3.2] 真人实操记录，任务 18 [A3.1] 公开资料检索

**供计算指标**：M10（现有平台满意度）、D1（明确差异化功能点数）

**产出任务**：任务 19 [A3.2]（A 轨 `[文档]`），汇总上述三方输入

## 表头

```
platform,job_types_covered,agent_job_availability,skill_tag_support,differentiation,satisfaction_score,evidence_url
```

模板文件：[templates/competitors.csv](templates/competitors.csv)

## 字段定义

| 字段 | 类型 | 必填 | 取值 | 说明 |
|---|---|---|---|---|
| `platform` | text | ✅ | — | 平台名，一行一平台 |
| `job_types_covered` | list | ✅ | `;` 分隔 | 覆盖的职位类型 |
| `agent_job_availability` | text | ✅ | 自由文本 | Agent 岗位的可用性 |
| `skill_tag_support` | text | ✅ | 自由文本 | 是否支持技能标签筛选及支持粒度 |
| `differentiation` | list | ❌ | `;` 分隔 | **AgentJobs 相对该竞品的差异化功能点**，且须在垂直竞品基准下成立（见下方「D1 计点规则」）。**D1 对此列去重计数** |
| `satisfaction_score` | float | ❌ | 1.0–10.0 | **M10**：开发者对现有平台的满意度。**未实操打分的平台留空**，M10 按已打分平台的均值计算 |
| `evidence_url` | text | ✅ | URL 或截图路径 | 证据支撑 |

> **`satisfaction_score` 为何可空**：M10 需要真人实操打分，公开资料无法得出（见 `competitors-research.md` 的硬约束 2）。任务 19 [A3.2] 的输入天然是「公开资料已填、满意度待实操」的状态；若该列必填，schema 校验会先于指标计算失败（退出码 2），整张打分表根本跑不出来。
>
> **`differentiation` 为何可空**：D1 计点须逐条给出基准证据，未完成时不填推测值（与「无证据的字段留空」是同一条硬约束）。

## 指标口径

- **M10 当前平台满意度** = `satisfaction_score` 均值（**仅统计已打分的平台**）。**越低越好**（通过值 ≤ 5/10）
- **D1 明确差异化功能点数量** = `differentiation` 列跨行去重后的项数（通过值 ≥ 3）

> **M10 是低优指标**：判定阶梯中 M10 的失败值写作「≥ 7/10」，脚本据此自动识别方向，
> 无需额外配置。同理 M7 是高优指标（难度越高说明企业越痛）。

## D1 计点规则（2026-10-31 裁定）

`validation-metrics.md` 的 D1 条目已把计量基准从「通用平台」改为**垂直竞品**。本表必须按该基准执行，否则第 4 周的判定会得出「差异化已成立」的错误结论。

### 基准竞品

计点的参照物是**已在运营的 Agent 垂直招聘平台**（来源：`competitors-research.md`）：

| 平台 | 规模（官方自述） | 对 D1 计点的影响 |
|---|---|---|
| `agenticcareers.co` | 2,962 岗位 / 890 公司 | 已提供 agentic 专属岗位分面、资历/薪酬披露/远程/新鲜度/雇主段位筛选、公司阶段与栈筛选 |
| `agenticengineeringjobs.com` | 200 岗位 | 已提供 7 类 agentic 岗位分类法（AgentOps / Prompt / Agent Architect 等）、按岗位公布薪资带 |
| `agentic-engineering-jobs.com` | 500+ 岗位 | 已提供 agentic-stack 筛选：LangGraph、CrewAI、Pydantic AI、RAG、multi-agent、LLM observability、evals |
| `ai-native-builder.com` | 300 岗位 | 已提供工具标签：Claude Code、Codex、LangGraph、Cursor、LangChain |
| `aidevboard.com` | 9,384 岗位 / 57 stack | 已提供 `ai-agents` 角色分类、stack 标签与 `match_jobs(skills)` 技能匹配 |

### 计点规则

1. **一个功能点只有满足「垂直竞品未提供」或「垂直竞品提供得更差」时才计入 D1。**
2. **「技能标签筛选」「Agent 岗位专区」相对通用平台是差异点，但垂直竞品已经提供且粒度更细——不计入。** 这两类恰恰是原参照系下最容易被计入的两点，也正是基准变更要排除的对象。
3. **每个计入的点须给出三段式证据**：`证据类型`（竞品已有 / 竞品缺失 / 竞品更弱）+ `竞品名` + `evidence_url`（或截图路径）。只写「我们有而他们没有」不算证据。
4. **措辞须一致**（受控词表）：否则去重失效——「支持 Agent 技能标签筛选」与「有技能筛选功能」不会被识别为同一项。建议由任务 19 维护一份受控词表，并在每次填表后核对。
5. **阈值不变**：通过值 ≥ 3、理想值 ≥ 5、失败值 0。基准变更只改变**什么算差异化点**，不改变**要几个**。

### 与 M10 的分工

D1 回答「相对垂直竞品我们凭什么不同」，M10 回答「现有平台有多难用」。二者不同源、不可互相替代：M10 来自开发者实操打分，D1 来自功能对比。

## 预填表：公开资料部分已就绪

`competitors-prefill.csv`（本目录）是任务 18 [A3.1] 检索结果的**结构化预填**，36 行平台（垂直 16 / 通用 6 / 技术 14），已填 5 列：

| 列 | 状态 |
|---|---|
| `platform`、`job_types_covered`、`agent_job_availability`、`skill_tag_support`、`evidence_url` | ✅ 已填（全部来自公开资料，附来源 URL） |
| `satisfaction_score` | ⬜ 留空——须 H3.1 / H3.2 真人实操打分 |
| `differentiation` | ⬜ 留空——须按上方「D1 计点规则」逐条给出基准证据 |

**用法**：

```bash
cp validation/schemas/competitors-prefill.csv validation/data/competitors.csv
# 填完两列后即可直接跑指标脚本（无需再手工录入 36 行 × 7 字段）
python3 validation/compute_metrics.py --data-dir validation/data
```

任务 19 [A3.2] 在此基础上补两列、补 H3.1/H3.2 的实操笔记，并产出 D1 的逐点证据清单。

## 证据要求

- **每行必须有 `evidence_url` 或截图路径**。无证据的字段**留空，不得填写推测值**（任务 19 的硬约束）。
- `differentiation` 各项应使用**一致的措辞**，否则去重会失效——
  「支持 Agent 技能标签筛选」与「有技能筛选功能」不会被识别为同一项。
  建议由任务 19 维护一份**受控词表**。

## M11 不在本表（2026-10-11 裁定）

任务 15 [A1.2] 曾把 **M11 差异化需求**归给本表，但：

- M11 的定义是「提出 ≥3 项差异化需求的**用户**比例」（`validation-metrics.md`）
- 本表是**平台级**数据，一行一平台，统计单元是平台而非用户

两者统计单元不匹配。**裁定：M11 数据源改为 `survey_responses.csv` 的
`differentiation_needs` 列**（问卷多选题），详见
[survey_responses.md](survey_responses.md)。

本表仍产出 **M10**（满意度均值）与 **D1**（差异化功能点去重计数）。