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
| `differentiation` | list | ✅ | `;` 分隔 | 观察到的差异化功能点。**D1 对此列去重计数** |
| `satisfaction_score` | float | ✅ | 1.0–10.0 | **M10**：开发者对现有平台的满意度 |
| `evidence_url` | text | ✅ | URL 或截图路径 | 证据支撑 |

## 指标口径

- **M10 当前平台满意度** = `satisfaction_score` 均值。**越低越好**（通过值 ≤ 5/10）
- **D1 明确差异化功能点数量** = `differentiation` 列跨行去重后的项数（通过值 ≥ 3）

> **M10 是低优指标**：判定阶梯中 M10 的失败值写作「≥ 7/10」，脚本据此自动识别方向，
> 无需额外配置。同理 M7 是高优指标（难度越高说明企业越痛）。

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