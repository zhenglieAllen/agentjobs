# validation —— 验证数据管道

任务 **15 [A1.2]** 的产出。这是 AgentJobs 30 天验证期的**关键路径起点**：
其 schema 必须在任务 1/4/6/7（H1.1 / H2.1 / H3.1）采集数据**之前**定稿，
否则访谈与问卷数据无法聚合，M4–M12 全部不可计算。

## 快速开始

```bash
# 1. 从模板复制 5 份数据文件
mkdir -p validation/data
cp validation/schemas/templates/*.csv validation/data/

# 2. 填充数据（字段定义见 validation/schemas/*.md）

# 3. 跑指标计算
python3 validation/compute_metrics.py --data-dir validation/data

# JSON 输出（供仪表盘消费）
python3 validation/compute_metrics.py --data-dir validation/data --json

# 测试
python3 -m unittest discover -s validation/tests
```

退出码：`0` = 未命中失败值；`1` = 命中失败值（验证失败）；`2` = schema 校验错误。

## 目录结构

```
validation/
├── compute_metrics.py          # 指标计算脚本（标准库，无第三方依赖）
├── interview-guides.md         # 创始人执行物料：H1.1 开发者 / H2.1 企业访谈提纲
├── survey-distribution.md      # 创始人执行物料：H1.3 问卷投放方案（含 M3 埋点前提）
├── schemas/
│   ├── subscribers.md          # 6 份 schema 文档（含字段定义、指标口径、约束）
│   ├── interviews.md
│   ├── companies.md
│   ├── survey_responses.md
│   ├── social_posts.md
│   ├── competitors.md
│   ├── competitors-research.md # 任务 18 [A3.1] 竞品公开资料检索结果（36 个平台）
│   └── templates/*.csv         # 表头模板（可直接复制填写）
└── tests/test_compute_metrics.py
```

## 创始人执行物料（`interview-guides.md` / `survey-distribution.md`）

这两份是**给创始人用的作业指导书**，不是给脚本用的。目的是让采集到的数据
**直接可聚合**，不必在第 5 周回头返工：

| 文件 | 对应任务 | 覆盖的指标 | 关键提示 |
|---|---|---|---|
| `interview-guides.md` | 1 [H1.1]、4 [H2.1] | M4、M5、S1 / M6–M9、S2 | 痛点措辞必须与问卷 Q7 一字不差；M6 与 M8 必须分开问 |
| `survey-distribution.md` | 3 [H1.3] | S3、M3、M4、M11、M12 | **投放前先确认工具支持「开始」埋点**，否则 M3 不可计算 |

> 物料中已标注两处**竞品检索带来的新风险**（见 `schemas/competitors-research.md`）：
> ① M6 与 M8 若不分开问，5 家样本下三道供给关卡会退化成一道；
> ② 问卷 Q9 的选项相对**已运营的垂直竞品**可能已过时，M11 会被系统性压低，
> 解读时须结合竞品证据，不可直接判失败。

## 数据流向

| CSV | 产出任务 | 轨道 | 供计算指标 |
|---|---|---|---|
| `subscribers.csv` | 任务 14 [A1.1] | 🟢 A `[代码]` | M1 |
| `interviews.csv` | 任务 1 [H1.1] | 🔴 H 人工 | S1、M4（交叉校验）、M5 |
| `companies.csv` | 任务 4 [H2.1] | 🔴 H 人工 | S2、M6–M9 |
| `survey_responses.csv` | 任务 3 [H1.3] 投放 + 任务 16 [A1.3] 设计 | 🔴 H 投放 / 🟢 A `[文档]` 设计 | S3、M3、M4（主口径）、M11、M12 |
| `social_posts.csv` | 创始人手工记录 | — | M2 |
| `competitors.csv` | 任务 19 [A3.2] | 🟢 A `[文档]` | M10、D1 |

> `competitors.csv` 的**公开资料部分已由任务 18 [A3.1] 完成**（见
> `schemas/competitors-research.md`，36 个平台）。任务 19 [A3.2] 负责把它与
> 任务 6/7（H3.1 / H3.2）的真人实操记录合并为最终对比表。
> **两处关键缺口留给实操**：`satisfaction_score` 全部留空（M10 需要真人打分，
> 公开资料无法得出），以及 P0 级的 20 项待验证清单。

## 三条不可违反的约束

### 1. 阈值不硬编码

全部阈值在运行时从 `.spec-workflow/specs/agentjobs/validation-metrics.md`
的「判定阶梯」表格解析。改文档 → 脚本自动跟随，不需要改代码。

测试 `test_thresholds_follow_document_changes` 通过修改文档副本并重新解析来守住这条约束。

指标方向（高优/低优）同样自动识别：判定阶梯中 M10 的失败值写作「≥ 7/10」，
说明它越低越好；M7 写作「< 5/10」，越低越差。二者无需额外配置。

### 2. 缺数据不等于 0

- **缺列** → 报错退出，提示应有的表头
- **枚举值非法**（如 `ab_variant = Z`）→ 报错退出，列出允许值
- **数值越界**（如 `satisfaction_score = 12`）→ 报错退出
- **分母为 0** → 判定为「无数据源」，**不按 0 处理**（否则会被误判为失败）

### 3. 样本量门槛不判失败

S1/S2/S3 未达标时，M4–M12 仍用已完成样本计算并输出，但会附带样本量提示，
不判失败。这遵循 `validation-metrics.md`「关于样本量的门槛语义」。

## 判定结论

| 结论 | 条件 |
|---|---|
| 验证失败 | 命中任一失败值 |
| 强力验证 | 全部指标达理想值 |
| 验证通过 | 全部指标达通过值及以上，无未达标项 |
| 未达标 | 无失败值命中，但存在指标落在通过值与失败值之间 |

两条附加规则：

- **D2 特殊规则**：D2 ≥ 1 可在其他指标未达标时单独支撑「继续」；D2 = 0 且
  M1–M12 中 ≥ 3 项未达标时输出 `risk-analysis.md` **风险 4（双边市场冷启动）**告警。
- **暂定结论**：若存在无数据源的指标，结论标注为暂定，并列出待补齐项。

## 数据源缺口裁定（2026-10-11）

A1.2 实现后经指标可计算性审查，发现 4 处缺口并已裁定落地：

| 缺口 | 裁定 | 影响 |
|---|---|---|
| **M6** 无字段承载 | `companies.csv` 新增 `interested_in_platform`（布尔） | 任务 4 [H2.1] 访谈提纲须补该问题，并与 M8 明确区分 |
| **M11** 统计单元错配 | 数据源由 `competitors.csv`（平台级）改为 `survey_responses.csv` 的 `differentiation_needs`（用户级） | 任务 16 [A1.3] 问卷须新增该多选题——**漏做将导致 M11 永久无数据源** |
| **M2** 无数据源 | 新增第 6 份 schema `social_posts.csv` | 创始人手工记录；`impressions = 0` 的帖子须跳过并提示 |
| **D2** 无数据源 | **明确声明验证期不评估**，D2 判定阶段为平台期 | H5.1 结论须标注「未含 D2 终端证据」；风险 4 告警按「D2 缺席」而非「D2 = 0」触发 |

D2 的缺席是**设计预期**而非缺口，因此脚本不将其计入「暂定」警告，但每次输出结论时
都会附带终端证据缺失的声明。

**明确不做的事**：不用任务 5 [H2.2] 的 seeding 就绪度替代 D2。那是意向证据，
冒充终端证据会使「终端证据可单独支撑继续」的语义退化为「意向证据可单独支撑继续」，
`risk-analysis.md` 风险 4 的防护逻辑失效。