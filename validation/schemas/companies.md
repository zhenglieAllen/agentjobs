# companies.csv —— 企业深度访谈结构化摘要

**权威来源**：任务 4 [H2.1]（创始人执行，H 轨）

**供计算指标**：S2（企业访谈数）、M6（主动联系意愿）、M7（招聘难度评分）、M8（承诺发布职位）、M9（预算准备度）

**产出任务**：任务 4 [H2.1] —— 创始人。agent **不得**代为标记本文件的数据完成状态。

## 表头

```
company_id,agent_projects,hiring_challenge,required_skills,interested_in_platform,has_budget,committed_to_post,difficulty_score,interview_date
```

模板文件：[templates/companies.csv](templates/companies.csv)

## 字段定义

| 字段 | 类型 | 必填 | 取值 | 说明 |
|---|---|---|---|---|
| `company_id` | text | ✅ | — | 企业匿名标识（如 `co-001`） |
| `agent_projects` | text | ✅ | 自由文本 | 企业现有的 Agent 项目情况 |
| `hiring_challenge` | text | ✅ | 自由文本 | 招聘中遇到的困难 |
| `required_skills` | list | ✅ | `;` 分隔 | 要求候选人具备的技能 |
| `interested_in_platform` | bool | ✅ | `true`/`false` | **M6 口径**：是否愿意使用专门平台。⚠️ 见下方「字段补齐说明」 |
| `has_budget` | bool | ✅ | `true`/`false` | **M9**：已有或计划招聘预算 |
| `committed_to_post` | bool | ✅ | `true`/`false` | **M8**：承诺在平台发布职位 |
| `difficulty_score` | float | ✅ | 1.0–10.0 | **M7**：招聘 AI Agent 开发者的自评难度 |
| `interview_date` | date | ✅ | ISO 8601 | 访谈日期 |

## 字段补齐说明

`interested_in_platform` 是任务 15 [A1.2] 实现阶段补齐的字段，**已追认**并写回
`tasks.md` 任务 15 的 schema 定义（2026-10-11 裁定）。

- **原因**：A1.2 原文写「`companies.csv` → 供 M6（有兴趣）」，但原字段集
  （`agent_projects` / `hiring_challenge` / `required_skills` / `has_budget` /
  `committed_to_post` / `difficulty_score`）中**没有任何字段能承载 M6 的口径**——
  `committed_to_post` 是 M8 的行为承诺，`has_budget` 是 M9 的预算，二者都不等价于「愿意使用专门平台」。
- **不采用的替代方案**：改用 `has_budget` 或 `committed_to_post` 近似。5 家企业的样本量下，
  M6/M8/M9 三项会高度共线，判定阶梯的三道供给关卡退化为一道，
  无法区分「有意愿但无预算」与「有预算但不承诺」这两类关键差异。
- **连带**：任务 4 [H2.1] 的访谈提纲须逐项采集 M6 口径，
  且须与 M8 明确区分（问「愿不愿意用这个平台」而非「是否承诺发布职位」）。

## 指标口径

- **S2** = 行数（通过值 ≥ 5）
- **M6** = `interested_in_platform == true` 占比（通过值 ≥ 40%）
- **M7** = `difficulty_score` 均值，**越高表示招聘越难**（通过值 ≥ 7/10）
- **M8** = `committed_to_post == true` 占比（通过值 ≥ 20%，基数为 5 时即 ≥ 1 家）
- **M9** = `has_budget == true` 占比（通过值 ≥ 60%）

> **M7 与 M10 量纲相反**：M7「难度」越高越好（企业越痛），M10「满意度」越低越好。
> 判定阶梯中 M10 的失败值写作「≥ 7/10」，脚本据此自动识别其为**低优指标**，
> 不需要额外配置。

## 与 H2.2 的关系

`committed_to_post == true` 只代表**口头承诺**，不构成供给。任务 5 [H2.2] 须另行产出
**具体可发布的职位内容草稿**，对应 `requirements.md` 验证期验收标准第 8 项。